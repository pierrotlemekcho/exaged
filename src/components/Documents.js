import React, { useEffect, useState, createRef } from "react";
import config from "config.js";
import axios from "axios";
import {
  Header,
  Container,
  Input,
  Image,
  Card,
  Modal,
  Icon,
  Button,
} from "semantic-ui-react";
import PdfPreview from "components/PdfPreview.js";

function Documents( {orderId}) {
  const api_url = config.api_url;

  const [folderFiles, setFolderFiles] = useState([]);
  const [currentFile, setCurrentFile] = useState(null);
  const [rotate, setRotate] = useState(0);
  const orderInput = createRef(null);

  async function fetchFolderContent(orderId) {
    let result = await axios.get(
      `${api_url}/commandes/${orderId}/files`
    );
    setFolderFiles(result.data);
  }

  useEffect(() => {
    fetchFolderContent(orderId);
  },[])

  function rotateToTheRight() {
    let newRotate = rotate + 90;
    if (newRotate >= 360) {
      newRotate = 0;
    }
    setRotate(newRotate);
  }

  return (
    <Container className="page-container">
      <Header as="h1"> Documents </Header>
      <Card.Group>
        {folderFiles.map((file) => (
          <Card onClick={() => setCurrentFile(file)}>
            <Image
              src={`${api_url}/commandes/${orderId}/thumbnail?filename=${file.filename}`}
            />
          </Card>
        ))}
      </Card.Group>

      {currentFile ? (
        <Modal
          onClose={() => setCurrentFile(null)}
          open={true}
          onOpen={() => setRotate(0)}
          size="fullscreen"
        >
          <Modal.Header>{currentFile.filename}</Modal.Header>
          <Modal.Content>
            {currentFile.mimetype === "application/pdf" ? (
              <PdfPreview rotate={rotate} fileUrl={`${api_url}/commandes/${orderId}/file_download?filename=${currentFile.filename}`} />
            ) : (
              <Image
                src={`${api_url}/commandes/${orderId}/file_download?filename=${currentFile.filename}`}
              />
            )}
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={rotateToTheRight}>
              <Icon name="redo" /> Faire Pivoter la page
            </Button>
            <Button color="black" onClick={() => setCurrentFile()}>
              Fermer
            </Button>
          </Modal.Actions>
        </Modal>
      ) : null}
    </Container>
  );
}

export default Documents;
