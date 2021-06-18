import React from 'react';
import './App.css';
import {
  Container,
  Image,
  Menu
} from 'semantic-ui-react'

import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import ExaCam from 'components/ExaCam.js'
import Documents from 'components/Documents.js';
import logo from 'logo.png'

import 'semantic-ui-css/semantic.min.css'

function App() {

  return (
    <Router>
      <Menu fixed='top' inverted>
        <Container>
          <Menu.Item as='a' header>
            <Image size='mini' src={logo} />
          </Menu.Item>
          <Menu.Item as='a' href='/'>ExaCAM</Menu.Item>
          <Menu.Item href="/documents "as='a'>Documents</Menu.Item>
        </Container>
      </Menu>
      <Switch>
        <Route path="/documents">
          <Documents />
        </Route>
        <Route path="/">
          <ExaCam />
        </Route>
      </Switch>

    </Router>
  );
}

export default App;
