import React from "react";
import "./App.css";
import { Container, Image, Menu } from "semantic-ui-react";

import { BrowserRouter as Router, Switch, Route, useLocation } from "react-router-dom";
import ExaCam from "components/ExaCam.js";
import Documents from "components/Documents.js";
import Plannif from "components/Plannif.js";
import logo from "logo.png";

import "semantic-ui-css/semantic.min.css";

// A custom hook that builds on useLocation to parse
// the query string for you.
function useQuery() {
  return new URLSearchParams(useLocation().search);
}


function App() {
  return (
    <Router>
      <AppInRouter />
    </Router>
  );
}

function  AppInRouter() {
  let query = useQuery();
  return (
    <>
      <Menu fixed="top" inverted>
        <Container>
          <Menu.Item as="a" header>
            <Image size="mini" src={logo} />
          </Menu.Item>
          <Menu.Item as="a" href="/">
            ExaCAM
          </Menu.Item>
          <Menu.Item href="/documents " as="a">
            Documents
          </Menu.Item>
          <Menu.Item href="/plannif " as="a">
            Plannif
          </Menu.Item>
        </Container>
      </Menu>
      <Switch>
        <Route path="/documents">
          <Documents orderId = {query.get("orderid")}/>
        </Route>
        <Route path="/plannif">
          <Plannif />
        </Route>
        <Route path="/">
          <ExaCam />
        </Route>
      </Switch>
    </>
  )
}

export default App;
