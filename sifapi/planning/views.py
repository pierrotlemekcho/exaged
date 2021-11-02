import io
from datetime import datetime

import cv2
from django.http import FileResponse
from pdf2image import convert_from_bytes
from PIL import Image
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import (action, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from planning import samba
from planning.models import Commande, LigneDeCommande, Operation, Tier, WebCam
from planning.renderers import JPEGRenderer
from planning.serializers import (AnonymousCommandeSerializer,
                                  AnonymousOrderLineSerializer,
                                  CommandeSerializer, OperationSerializer,
                                  OrderLineSerializer, TierSerializer,
                                  WebCamSerializer)

EXACT_STATUS_CLOSED = 21
EXACT_STATUS_CANCELLED = 45
EXACT_STATUS_OPEN = 12
EXACT_STATUS_PARTIAL = 20


@api_view(["GET"])
@permission_classes([IsAuthenticated])
# find out who is logged in
def me(request, format=None):
    content = {
        "user": str(request.user),  # `django.contrib.auth.User` instance.
        "auth": str(request.auth),  # None
    }
    return Response(content)


class WebCamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebCam.objects.all()
    serializer_class = WebCamSerializer

    @action(detail=True, methods=["get"], renderer_classes=[JPEGRenderer])
    def thumbnail(self, request, pk=None):
        webcam = self.get_object()
        video_capture = cv2.VideoCapture(f"{webcam.url}/profile3")
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (640, 375))
        return Response(cv2.imencode(".jpg", small_frame)[1].tobytes())

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def capture(self, request, pk=None):
        if int(pk) > 0:
            webcam = self.get_object()
            video_capture = cv2.VideoCapture(f"{webcam.url}/profile1")
            ret, frame = video_capture.read()
            image = io.BytesIO(cv2.imencode(".jpg", frame)[1].tobytes())
        else:
            image = request.data["file"]
        order_id = request.data["order_id"]
        smb_connection = samba.factory()
        if order_id:
            order_id = int(request.data["order_id"])
            order = Commande.objects.get(id=order_id)
            tier = order.exact_tier
            filename = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"//Workspace$/documents/32-Clients/{tier.exact_name}/C{order.exact_order_number}/{filename}.jpg"
        else:
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"//Documentsv7$/OFFICE One Documents/spool/{date}.jpg"
        samba.store_file_and_create_folders(smb_connection, filename, image)
        return Response({"filename": filename})


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TierSerializer
    queryset = (
        Tier.objects.filter(exact_is_sales=1, commande__exact_status=EXACT_STATUS_OPEN)
        .distinct()
        .order_by("exact_name")
    )


class CommandeViewSet(viewsets.ReadOnlyModelViewSet):
    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return CommandeSerializer

        return AnonymousCommandeSerializer

    queryset = Commande.objects.all().order_by("-id")
    filterset_fields = {"exact_tier_id": ["exact"], "exact_status": ["exact", "in"]}

    @action(detail=True, url_name="files")
    def files(self, request, **kwargs):
        order = self.get_object()
        smb_connection = samba.factory()
        folder_content = samba.list_path(smb_connection, order.folder_path)
        result = []
        for content in folder_content:
            if not content.isDirectory:
                full_path = f"{order.folder_path}/{content.filename}"
                mimetype = samba.find_file_mime_type(smb_connection, full_path)
                if mimetype.startswith("image") or mimetype == "application/pdf":
                    result.append(
                        {
                            "filename": content.filename,
                            "last_write_time": content.last_write_time,
                            "file_size": content.file_size,
                            "mimetype": samba.find_file_mime_type(
                                smb_connection, full_path
                            ),
                        }
                    )
        return Response(data=result)

    @action(detail=True, url_name="thumbnail")
    def thumbnail(self, request, **kwargs):
        THUMBNAIL_SIZE = (400, 400)
        order = self.get_object()
        smb_connection = samba.factory()
        filename = request.query_params.get("filename")
        folder_content = samba.list_path(smb_connection, order.folder_path)
        # Throw an error if file not a direct children
        next(x for x in folder_content if x.filename == filename)
        full_path = f"{order.folder_path}/{filename}"
        file_type = samba.find_file_mime_type(smb_connection, full_path)
        if file_type.startswith("image"):
            buffer_file = samba.retrieve_file(smb_connection, full_path)
            result = io.BytesIO()

            file = Image.open(buffer_file)
            file.thumbnail(THUMBNAIL_SIZE)
            file.save(result, "PNG", compress_level=9)
            result.seek(0)
            return FileResponse(result)
        elif file_type == "application/pdf":
            buffer_file = samba.retrieve_file(smb_connection, full_path)
            images = convert_from_bytes(
                buffer_file.read(), size=THUMBNAIL_SIZE[0], fmt="png"
            )
            image = images[0]
            result = io.BytesIO()
            image.save(result, "PNG", compress_level=9)
            result.seek(0)
            return FileResponse(result)
        return

    @action(detail=True, url_name="file_download")
    def file_download(self, request, **kwargs):
        order = self.get_object()
        smb_connection = samba.factory()
        filename = request.query_params.get("filename")
        folder_content = samba.list_path(smb_connection, order.folder_path)
        # Throw an error if file not a direct children
        next(x for x in folder_content if x.filename == filename)
        full_path = f"{order.folder_path}/{filename}"
        buffer_file = samba.retrieve_file(smb_connection, full_path)
        return FileResponse(buffer_file)


class OperationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OperationSerializer
    queryset = Operation.objects.all().order_by("-id")


# Only updat for now.
class BulkOrderLineViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = LigneDeCommande.objects.all()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return OrderLineSerializer

        return AnonymousOrderLineSerializer

    @action(detail=False, methods=["put"], url_name="bulk_update")
    def bulk_update(self, request, **kwargs):
        data = {  # we need to separate out the id from the data
            i["id"]: {k: v for k, v in i.items() if k != "id"} for i in request.data
        }

        for inst in self.get_queryset().filter(id__in=data.keys()):
            serializer = self.get_serializer(inst, data=data[inst.id], partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({})


class ClientCommandeViewSet(viewsets.ModelViewSet):
    serializer_class = CommandeSerializer

    def get_queryset(self):
        exact_tier_id = self.kwargs("exact_tier_id")
        return Commande.object.filter(
            exact_tier_id=exact_tier_id, exact_status=EXACT_STATUS_OPEN
        ).order_by("-exact_order_number")
