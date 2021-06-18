import React, { useEffect, useState, createRef } from 'react';
import config from 'config.js'
import axios from 'axios';
import {
  Header,
  Container,
  Input,
  Image,
  Card,
  Modal,
  Icon,
  Button
} from 'semantic-ui-react'
import PdfPreview from 'components/PdfPreview.js'

function Documents() {

  const api_url = config.api_url;

  const [selectedOrderNumber, setSelectedOrderNumber] = useState('');
  const [folderFiles, setFolderFiles] = useState([])
  const [currentFile, setCurrentFile] = useState(null)
  const [rotate, setRotate] = useState(0)
  const orderInput = createRef(null)



  async function fetchFolderContent() {
    let selectedOrderNumber = orderInput.current.inputRef.current.value;
    setSelectedOrderNumber(selectedOrderNumber);
    let result =  await axios.get(`${api_url}/folder/${selectedOrderNumber}`);
    setFolderFiles(result.data);
  }

  function rotateToTheRight() {
    let newRotate = rotate + 90;
    if (newRotate >= 360) {
      newRotate = 0;
    }
    setRotate(newRotate);
  }

  return (
    <Container className='page-container'>
      <Header as='h1'> Documents </Header>
      <Input action={{
        content: 'Chercher',
        onClick: fetchFolderContent
      }}
        placeholder='Chercher' 
        ref={orderInput}
      />
      <br />
      <br />
      <Card.Group>
        {folderFiles.map(file => 
          <Card onClick={() => setCurrentFile(file)}>
            <Image src={`${api_url}${file.thumbnail_url}`} />
          </Card>
        )}
      </Card.Group>

      {currentFile
        ?  <Modal
          onClose={() => setCurrentFile(null)}
          open={true}
          onOpen={() => setRotate(0)}
          size="fullscreen"
        >
          <Modal.Header>{currentFile.filename}</Modal.Header>
          <Modal.Content>
            {currentFile.mimetype === 'application/pdf'
             ? <PdfPreview rotate={rotate} fileUrl={currentFile.url} />
            : <Image src={currentFile.url}/>
            }
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={rotateToTheRight}>
              <Icon name="redo"/> Faire Pivoter la page
            </Button>
            <Button color='black' onClick={() => setCurrentFile()}>
              Fermer
            </Button>
          </Modal.Actions>
        </Modal>
        : null
      }
    </Container>
  );
}

export default Documents
