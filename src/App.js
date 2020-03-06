import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';
import { Header, Container, Segment, Image, Dropdown, Button, Grid, Message, List } from 'semantic-ui-react'
import 'semantic-ui-css/semantic.min.css'



let api_url = process.env.REACT_APP_API_URL || '';

function App() {

  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [selectedClientId, setSelectedClientId] = useState('');
  const [clients, setClients] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [lastImagePath, setLastImagePath] = useState('')

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

  async function fetchInvoices(selectedClientId) {
    if (!selectedClientId) {
      return;
    }
    let result = await axios.get(`${api_url}/client/${selectedClientId}/commandes`);
    setInvoices(result.data.map((invoice) => {
      return {
        key: invoice.id,
        text: `${invoice.order_number} - ${invoice.description}`,
        value: invoice.id
      }
    }));
  }

  async function savePicture() {
    if (isSaving) {
      return;
    }
    setIsSaving(true);
    setLastImagePath('');
    let result = await axios.post(`${api_url}/video_feed/${selectedCamera}/${selectedInvoiceId || 0}`);
    setLastImagePath(result.data.filename);
    setIsSaving(false);
  }

  useEffect(() => {
    fetchCameras();
    fetchClients();

  }, [])

  useEffect(() => {
    fetchInvoices(selectedClientId)
  }, [selectedClientId]);

  return (
    <Container>
      <Header as='h1'> ExaCAM </Header>
      <Message info>
        <Message.Header>Instructions</Message.Header>
        <List ordered>
          <List.Item>Choisir un camera en cliquant dessus</List.Item>
          <List.Item>Choisir un client</List.Item>
          <List.Item>Choisir une facture</List.Item>
          <List.Item>Sauvegarder l'image</List.Item>
        </List>
        <p>On peut aussi ne pas choisir de client et de facture et la photo sera sauvegardee dans le dossier "A trier"</p>
      </Message>
      <Segment>
        <div>
          <Image.Group size="medium">
            {
              cameras.map((camera) =>
                <Image src={`${api_url}/video_feed/${camera}`} className={(selectedCamera === camera) ? 'camera-selected': ''} alt={camera} onClick={() => setSelectedCamera(camera)}/>
              )
            }
        </Image.Group>

          Camera: selectionnee: {selectedCamera}
        </div>
      </Segment>
      <Segment>
        <Grid columns={3}>
          <Grid.Row>
            <Grid.Column>
              <Dropdown
                placeholder="Choisir un Client" selection search options={clients}
                onChange={(event, { value }) => {
                  setSelectedClientId(value);
                  setSelectedInvoiceId('');
                }}
              />
            </Grid.Column>
            <Grid.Column>
              <Dropdown
                placeholder="Choisir une Commande" selection search options={invoices}
                onChange={(event, { value }) => setSelectedInvoiceId(value)}
              />
            </Grid.Column>
            <Grid.Column>
              <Button loading={isSaving} primary onClick={savePicture}>Sauvegarder photo {selectedInvoiceId? '': 'A trier'}</Button>
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

export default App;
