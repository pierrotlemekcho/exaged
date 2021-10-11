import io
from datetime import datetime

import cv2
from django.shortcuts import render
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from planning import samba
from planning.models import Commande, LigneDeCommande, Tier, WebCam
from planning.renderers import JPEGRenderer
from planning.serializers import (CommandeSerializer, OrderLineSerializer,
                                  TierSerializer, WebCamSerializer)

EXACT_STATUS_CLOSED = 21
EXACT_STATUS_CANCELLED = 45
EXACT_STATUS_OPEN = 12
# Create your views here.


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
    serializer_class = CommandeSerializer
    queryset = Commande.objects.all().order_by("-id")
    filterset_fields = {"exact_tier_id": ["exact"], "exact_status": ["exact", "in"]}


## Only updat for now.
class BulkOrderLineViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderLineSerializer
    queryset = LigneDeCommande.objects.all()

    @action(detail=False, methods=["put"], url_name="bulk_update")
    def bulk_update(self, request, **kwargs):
        data = {  # we need to separate out the id from the data
            i['id']: {k: v for k, v in i.items() if k != 'id'}
            for i in request.data
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
