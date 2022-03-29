import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import App from './components/App/App';
import Explore from './components/Explore/Explore';
import Demo from './components/Demo/Demo';
import { Redirect } from 'react-router-dom';
import { read_cookie } from 'sfcookies';

const AppRoute = props => {
  return <App {...props} />;
};

const DashboardRoute = props => {
  if (read_cookie('userToken').length != 0) {
    return <Dashboard token={read_cookie('userToken')[0]} />;
  } else {
    return (
      <Redirect
        push
        to={{
          pathname: '/',
        }}
      />
    );
  }
};

const ExploreRoute = props => {
  if (read_cookie('userToken').length != 0) {
    return <Explore token={read_cookie('userToken')[0]} />;
  } else {
    return (
      <Redirect
        push
        to={{
          pathname: '/',
        }}
      />
    );
  }
};

export default () => (
  <BrowserRouter>
    <Switch>
      <Route exact path="/" component={AppRoute} />
      <Route path="/dashboard" exact component={DashboardRoute} />
      <Route path="/explore" exact component={ExploreRoute} />
      <Route path="/demo" exact component={Demo} />
    </Switch>
  </BrowserRouter>
);
