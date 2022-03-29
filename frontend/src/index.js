import React from 'react';
import ReactDOM from 'react-dom';
import * as serviceWorker from './config/serviceWorker';
import Routes from './Routes';
import './index.css';
import 'tailwindcss/dist/base.css';
import './components/App/App.css';

ReactDOM.render(
  <React.StrictMode>
    <Routes />
  </React.StrictMode>,
  document.getElementById('root')
);

//use this for testing
// ReactDOM.render(<UserInfo token="hi" />, document.getElementById('root'));
// ReactDOM.render(<PrivacyPolicy />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
