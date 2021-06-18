import React, { useEffect, useState } from 'react';
import {
  Header,
  Container,
  Segment,
  Image,
  Dropdown,
  Button,
  Grid,
  Message,
  List,
} from 'semantic-ui-react'
import axios from 'axios';
import config from 'config.js'
import Dropzone from 'react-dropzone'

function ExaCam() {

  const api_url = config.api_url;

  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [selectedClientId, setSelectedClientId] = useState('');
  const [clients, setClients] = useState([]);
  const [orders, setOrders] = useState([]);
  const [selectedOrderId, setSelectedOrderId] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [lastImagePath, setLastImagePath] = useState('')
  const [files, setFiles] = useState([])

  async function fetchCameras() {
    let result =  await axios.get(`${api_url}/cameras`);
    setCameras(result.data);
    setSelectedCamera(result.data[0]);
  }

  async function fetchClients() {
    let result = await axios.get(`${api_url}/clients`);
    setClients(result.data.map((client) => {
      return { key: client.id , text: client.name,  value:client.id };
    }));
  }

  async function fetchOrders(selectedClientId) {
    let orders = [];
    if (selectedClientId) {
      let result = await axios.get(`${api_url}/client/${selectedClientId}/commandes`);
      orders = result.data.map((order) => {
        return {
          key: order.id,
          text: `${order.order_number} - ${order.description}`,
          value: order.id
        }
      });
    }
    setOrders(orders);
  }

  async function savePicture() {
    if (isSaving) {
      return;
    }

    setIsSaving(true);
    const url =`${api_url}/video_feed/${selectedCamera}/${selectedOrderId || 0}`
    let result;
    if (selectedCamera === 'custom-file') {
      var formData = new FormData();
      formData.append("file", files[0]);
      result = await axios.post(url, formData, {
        headers : {
          'Content-Type': 'multipart/form-data'
        }
      });
    } else {
      result = await axios.post(url);
    }
    setLastImagePath('');
    setLastImagePath(result.data.filename);
    setIsSaving(false);
  }

  useEffect(() => {
    fetchCameras();
    fetchClients();
  }, [])

  useEffect(() => {
    fetchOrders(selectedClientId)
  }, [selectedClientId]);

  return (
      <Container className='page-container'>
        <Header as='h1'> ExaCAM </Header>
        <Message info>
          <Message.Header>Instructions</Message.Header>
          <List ordered>
            <List.Item>Choisir une image en cliquant sur une camera ou en téléchargeant une manuellement</List.Item>
            <List.Item>Choisir un client</List.Item>
            <List.Item>Choisir une commande</List.Item>
            <List.Item>Sauvegarder l'image</List.Item>
          </List>
          <p>On peut aussi ne pas choisir de client et de commande et la photo sera sauvegardée dans le dossier "A trier"</p>
        </Message>
        <Segment>
          <div>
            <Image.Group size="medium">
              {
                cameras.map((camera) =>
                  <Image src={`${api_url}/video_feed/${camera}`} className={(selectedCamera === camera) ? 'camera-selected': ''} alt={camera} onClick={() => setSelectedCamera(camera)}/>
                )

              }
              {
                files.map(file => <Image src={URL.createObjectURL(file)} className={(selectedCamera === 'custom-file') ? 'camera-selected': ''} onClick={() => setSelectedCamera('custom-file')}/>)
              }
            </Image.Group>

            Camera selectionnee: {selectedCamera}
          </div>
        </Segment>
        <Dropzone accept={'image/*'} multiple={false} onDrop={acceptedFiles => {
          setFiles(acceptedFiles);
          setSelectedCamera('custom-file');

        }}>
          {({getRootProps, getInputProps}) => (
            <section>
              <div {...getRootProps()}>
                <input {...getInputProps()} />
                <button className="ui fluid button yellow">Ajouter une photo manuellement</button>
              </div>
            </section>
          )}
        </Dropzone>
        <Segment>
          <Grid stackable columns={3}>
            <Grid.Row>
              <Grid.Column>
                <Dropdown
                  value={selectedClientId}
                  placeholder="Choisir un Client" selection search options={clients}
                  clearable
                  onChange={(_, { value }) => {
                    setSelectedClientId(value);
                    setSelectedOrderId('');
                  }}
                />
              </Grid.Column>
              <Grid.Column>
                <Dropdown
                  clearable
                  value={selectedOrderId}
                  placeholder="Choisir une Commande" selection search options={orders}
                  onChange={(_, { value }) => {
                    setSelectedOrderId(value)
                  }}
                />
              </Grid.Column>
              <Grid.Column>
                <Button loading={isSaving} primary onClick={savePicture}>Sauvegarder photo {selectedOrderId? '': 'A trier'}</Button>
              </Grid.Column>
            </Grid.Row>
          </Grid>

        </Segment>
        {lastImagePath &&
        <Message attached='bottom' positive>
          Image enregistree sous: {lastImagePath}
        </Message>
        }

      </Container>
  );
}

export default ExaCam;
