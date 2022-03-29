import React, { useEffect } from 'react';
import ReactGA from 'react-ga';
import clsx from 'clsx';
import {
  makeStyles,
  CssBaseline,
  Box,
  AppBar,
  Container,
  Grid,
} from '@material-ui/core';
import BugsBanner from './BugsBanner';
import CustomizedDialogs from '../Table/NewCompanyModal';
import DuplicateCustomizedDialogs from '../Table/DuplicateCompanyModal';
import Copyright from '../misc/Copyright';
import SimpleDialog from './SimpleDialog';
import Board from 'react-trello';
import NewCardForm from './CustomCard';
import NewTodoForm from './TodoForm';
import CompanyModal from '../Shared/CompanyModal';
import CustomCard from './CustomCardTile';
import Navbar from '../Shared/Navbar';
import AlertDialog from './AlertDialog';
import TransitionAlerts from './TransitionAlerts';
import Confetti from 'react-confetti';
import moment from 'moment';
import { Redirect } from 'react-router-dom';
import { delete_cookie } from 'sfcookies';
import { isMobile } from 'react-device-detect';
import { pipToIndex, lookupStage, getQuery } from '../../helpers/utils';
import SimpleModal from './SimpleModal';
import { useLocation } from 'react-router-dom';

function updateLogin(tokenToUse) {
  const backendData = {
    token: tokenToUse,
  };
  const url = process.env.REACT_APP_USER_LOGIN;
  fetch(url, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });
}

const drawerWidth = 240;

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
    flexGrow: 1,
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
    minHeight: 36,
    background: '#ffffff',
    borderTopWidth: 'thick',
    borderTopColor: '#3c049c',
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
    background: '#ffffff',
    // color: '#000000',
    margin: theme.spacing(1),
  },
  navigation: {},
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(1),
    flexGrow: 1,
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(0),
    background: '#f0f1f3',
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  banner: {
    borderStyle: 'thick',
    backgroundColor: 'pink',
  },
  fixedHeight: {
    height: 240,
  },
  todoBoard: {
    borderRightWidth: 'thin',
    borderRightColor: '#cccccc',
    marginRight: '55px',
  },
  todoBoardMobile: {
    borderBottomWidth: 'thin',
    borderBottomColor: '#cccccc',
    marginBottom: '10px',
    height: 'auto',
  },
  companiesBoard: {
    marginLeft: '-45px',
  },
  companiesBoardMobile: {
    marginLeft: '0',
  },
}));

function titleCase(str) {
  return str
    .split(' ')
    .map(item => item.charAt(0).toUpperCase() + item.slice(1).toLowerCase())
    .join(' ');
}

function filterByTitle(jsonObject, id) {
  return jsonObject.filter(function(jsonObject) {
    return jsonObject['title'] == id;
  })[0];
}

function filterById(jsonObject, id) {
  return jsonObject.filter(function(jsonObject) {
    return jsonObject['id'] == id;
  })[0];
}

function filterByCID(array, cid) {
  try {
    return array.filter(item => {
      return item[0] === cid;
    })[0][2];
  } catch {
    return -1;
  }
}

function checkStage(stage) {
  if (stage in lookupStage) {
    return true;
  }
  return false;
}

function getDisplayedDeadline(deadline) {
  let momentDeadline = moment(deadline, 'YYYY-MM-DD');
  if (
    deadline == null ||
    momentDeadline.diff(moment('1970-01-01', 'YYYY-MM-DD')) == 0
  ) {
    return '';
  }
  let momentStartOfDay = moment().startOf('day');
  let momentDelta = moment.duration(momentDeadline.diff(momentStartOfDay));
  let humanReadableDeadline;
  if (momentDelta.months() > 1 || momentDelta.years() >= 1) {
    humanReadableDeadline = momentDeadline.format('MMMM Do YYYY');
  } else {
    humanReadableDeadline = momentDeadline.format('MMMM Do');
  }
  let relativeDeadline = momentDeadline.fromNow();
  let displayedDeadline = relativeDeadline + ', ' + humanReadableDeadline;
  return displayedDeadline;
}

//create todo date
function createTodoData(todoResult, lanes) {
  const cards = lanes[0].cards;

  // tid is 0
  // company is 1
  // deadline is 2
  // task is 3
  for (let i = 0; i < todoResult.length; i++) {
    const tid = todoResult[i][0];
    const company = todoResult[i][1];
    const deadline = getDisplayedDeadline(todoResult[i][2]);
    const task = todoResult[i][3];
    cards.push({
      company: company,
      deadline: deadline,
      task: task,
      id: 'Todo' + String(i + 1),
      tid: tid,
    });
  }
}

//create kanban data from query result
function createKanbanData(queryResult, lanes, real_login_time) {
  for (var i = 0; i < queryResult.length; i++) {
    if (!checkStage(queryResult[i][pipToIndex.stage])) {
      continue;
    }
    let stage = titleCase(lookupStage[queryResult[i][pipToIndex.stage]]);
    let company = queryResult[i][pipToIndex.company_name];
    let cid = queryResult[i][pipToIndex.cid];
    let lane = filterByTitle(lanes, stage);
    let cards = lane['cards'];
    let j = cards.length + 1;
    let curr_pid = queryResult[i][pipToIndex.pid];
    let notes = queryResult[i][pipToIndex.notes];
    let timestamp = queryResult[i][pipToIndex.timestamp];
    let recruiterName = queryResult[i][pipToIndex.recruiter_name];
    let recruiterEmail = queryResult[i][pipToIndex.recruiter_email];
    let link = queryResult[i][pipToIndex.challenge_link];
    if (queryResult[i][pipToIndex.active]) {
      cards.push({
        description: notes,
        draggable: true,
        id: 'Card' + String(j),
        laneId: lane['id'],
        title: company,
        pid: curr_pid,
        recruiterName: recruiterName,
        recruiterEmail: recruiterEmail,
        link: link,
        cid: cid,
        timestamp: timestamp,
        lastLogin: real_login_time,
      });
    }
  }
}

//returns true if new company already in the pipelines table
function checkCurrentCompanies(data, company) {
  var allCompanies = getAllCompaniesInTable(data);
  for (let i = 0; i < allCompanies.length; i++) {
    if (company == allCompanies[i]) {
      return true;
    }
  }
  return false;
}

function getAllCompaniesInTable(data) {
  var result = [];
  var lanes = data.lanes;
  for (var i = 0; i < lanes.length; i++) {
    var cards = lanes[i].cards;
    for (var k = 0; k < cards.length; k++) {
      result.push(cards[k].title);
    }
  }
  return result;
}

export default function Dashboard(props) {
  //components for modal popup for new company suggestion
  const [name, setName] = React.useState('');
  const location = useLocation();
  const todo_data = {
    lanes: [
      {
        id: 'lane0',
        title: 'To Do',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#FFFFFF',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#FFFFFF',
          borderBottom: '0px',
        },
        cards: [],
      },
    ],
  };
  const data = {
    lanes: [
      {
        id: 'lane0',
        title: 'Application',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#8fcbcc',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#8fcbcc',
          borderBottom: '0px',
        },
        cards: [],
      },
      {
        id: 'lane1',
        title: 'Referral',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#8fcbcc',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#8fcbcc',
          borderBottom: '0px',
        },
        cards: [],
      },
      {
        id: 'lane2',
        title: 'Coding Challenge',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#a8dee0',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#a8dee0',
          borderBottom: '0px',
        },
        cards: [],
      },
      {
        id: 'lane3',
        title: 'Interview',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#f9e2ae',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#f9e2ae',
          borderBottom: '0px',
        },
        cards: [],
      },
      {
        id: 'lane5',
        title: 'Offer',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#fbc78d',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#fbc78d',
          borderBottom: '0px',
        },
        cards: [],
      },
      {
        id: 'lane6',
        title: 'Rejection',
        style: {
          backgroundColor: '#ffffff',
          borderTopWidth: 'thick',
          borderTopColor: '#c1bbdd',
        },
        cardStyle: {
          backgroundColor: '#f3f3f3',
          fontFamily: 'Lato',
          borderLeftWidth: 'thin',
          borderLeftColor: '#c1bbdd',
          borderBottom: '0px',
        },
        cards: [],
      },
    ],
  };

  const [openSimple, setOpenSimple] = React.useState(false);

  const handleOpenSimple = name => {
    setName(name);
    setOpenSimple(true);
  };

  const handleCloseSimple = () => {
    setOpenSimple(false);
  };

  const [deleteOpen, setDeleteOpen] = React.useState(false);
  const [cardToDelete, setCardToDelete] = React.useState(null);
  const handleDeleteClickOpen = () => {
    setDeleteOpen(true);
  };

  const handleDeleteCloseCancel = () => {
    setDeleteOpen(false);
  };

  const handleDeleteClose = (e, card) => {
    setDeleteOpen(false);
    let url = process.env.REACT_APP_DASHBOARD_DELETE;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(card),
    }).then(response => {
      if (response.status == 200) {
        getQuery('pipeline_uid', props.token, setQuery);
        getQuery('todo', props.token, setTodo);
      }
    });
  };

  const [openInfo, setOpenInfo] = React.useState(false);
  const [openSettings, setOpenSettings] = React.useState(false);
  const [openDuplicateInfo, setDuplicateInfo] = React.useState(false);
  const [cardInfo, setCardInfo] = React.useState(null);
  const [newOffer, setNewOffer] = React.useState({ flag: false, offer: false });
  const [confetti, setConfetti] = React.useState(false);
  const [modalOpenTime, setModalOpenTime] = React.useState(null);

  const handleOpenInfo = () => {
    setOpenInfo(true);
  };

  const handleCloseInfo = () => {
    setOpenInfo(false);
  };

  const handleOpenDuplicateInfo = () => {
    setDuplicateInfo(true);
  };

  const handleCloseDuplicateInfo = () => {
    setDuplicateInfo(false);
  };

  const handleOpenSettings = e => {
    e.preventDefault();
    setOpenSettings(true);
  };

  const handleCloseSettings = () => {
    setOpenSettings(false);
  };

  const [companyModal, setCompanyModal] = React.useState(false);
  const handleCompanyModalOpen = card => {
    setModalOpenTime(moment());
    setCardInfo(card);
  };

  useEffect(() => {
    if (cardInfo !== null) {
      setCompanyModal(true);
    }
  }, [cardInfo]);

  useEffect(() => {
    if (newOffer.offer === true) {
      setTimeout(() => setNewOffer({ offer: false, flag: true }), 10000);
      setTimeout(() => setConfetti(false), 5000);
    }
  }, [newOffer]);

  const handleCompanyModalClose = () => {
    getQuery('pipeline_uid', props.token, setQuery);
    let time_diff = moment().diff(modalOpenTime, 'seconds');
    ReactGA.event({
      category: 'Company Modal',
      action: 'Viewed',
      label: cardInfo.cid,
      value: time_diff,
    });
    setCompanyModal(false);
  };

  const handleCardAdd = (card, laneId) => {
    let uid = userInfo[0][0];
    let token = props.token;
    let company_name = card.title;
    let notes = card.description;
    let stage_num = laneId.replace(/^\D+/g, '');
    let inTable = checkCurrentCompanies(data, company_name);
    if (inTable) {
      handleOpenDuplicateInfo();
      getQuery('pipeline_uid', props.token, setQuery);
      return;
    }
    let backendData = {
      token: token,
      uid: uid,
      company_name: company_name,
      stage: stage_num,
      notes: notes,
    };
    let url = process.env.REACT_APP_DASHBOARD_ADD;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    }).then(response => {
      if (response.status == 200) {
        response.json().then(res_json => {
          let pid = res_json['pid'];
          card.pid = pid;
        });
        getQuery('pipeline_uid', props.token, setQuery);
        return;
      } else if (response.status == 201) {
        handleOpenInfo();
        getQuery('pipeline_uid', props.token, setQuery);
        return;
      }
    });
  };

  const handleTodoAdd = (card, laneId) => {
    var token = props.token;
    let backendData = {
      company: card.company,
      task: card.task,
      deadline: card.deadline,
      token: token,
    };
    let url = process.env.REACT_APP_TODO_ADD;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    }).then(response => {
      if (response.status == 200) {
        response.json().then(res_json => {
          let tid = res_json['tid'];
          card.tid = tid;
        });
        getQuery('todo', props.token, setTodo);
      }
    });
  };

  const handleCardDelete = (cardId, laneId) => {
    const token = props.token;
    const lane = filterById(data.lanes, laneId);
    const card = filterById(lane.cards, cardId);
    const backendData = {
      token: token,
      pid: card.pid,
    };
    setCardToDelete(backendData);
    setDeleteOpen(true);
  };

  const handleTodoDelete = (cardId, laneId) => {
    const token = props.token;
    const lane = todo_data.lanes[0];
    const card = filterById(lane.cards, cardId);
    const backendData = {
      token: token,
      tid: card.tid,
    };
    let url = process.env.REACT_APP_TODO_DELETE;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    });
  };

  const handleCardMoveChangeStage = (fromLaneId, toLaneId, cardId, index) => {
    const fromLane = filterById(data.lanes, fromLaneId);
    const card = filterById(fromLane.cards, cardId);
    if (toLaneId === 'lane5') {
      setNewOffer({ offer: true, flag: false });
      setConfetti(true);
    }
    const token = props.token;
    const stage_num = toLaneId.replace(/^\D+/g, '');
    const backendData = {
      token: token,
      pid: card.pid,
      company: card.title,
      stage: stage_num,
    };
    const url = process.env.REACT_APP_DASHBOARD_EDIT;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    }).then(response => {
      if (response.status == 200) {
        getQuery('pipeline_uid', props.token, setQuery);
        return;
      }
    });
  };

  const handleCardClick = (cardId, metadata, laneId) => {
    var lane = filterById(data.lanes, laneId);
    var card = filterById(lane.cards, cardId);
    handleCompanyModalOpen(card);
  };

  const handleCardUpdate = (laneId, cardId) => {};

  //components for queries
  const [queryResult, setQuery] = React.useState(null);
  const [todoResult, setTodo] = React.useState(null);
  const [companyResult, setCompanies] = React.useState(null);
  const [userInfo, setUserInfo] = React.useState(null);
  const [redemptionPoints, setRedemptionPoints] = React.useState(null);
  let token = props.token;
  const classes = useStyles();
  //last login time, will pass into editabletable
  let real_login_time;

  //perform a check to see if we have succesfully queried the data yet.
  //if so we will increment our count to see if its the first or not, and document the last login time, before we overwrite it with our api
  if (
    !!queryResult &&
    queryResult.length > 0 &&
    queryResult[0][pipToIndex.user_email]
  ) {
    real_login_time = queryResult[0][pipToIndex.login_time];
  }

  useEffect(() => {
    getQuery('todo', props.token, setTodo);
    getQuery('companies', props.token, setCompanies);
    getQuery('pipeline_uid', props.token, setQuery);
    getQuery('user_info', props.token, setUserInfo);
    updateLogin(props.token);
    const showReferralModal =
      localStorage.getItem('showReferralModal') === 'true';
    if (!!location.state && !!location.state.referral && showReferralModal) {
      handleOpenSimple(location.state.referral);
      localStorage.setItem('showReferralModal', false);
    }
  }, []);

  useEffect(() => {
    if (!!userInfo) {
      setRedemptionPoints(!!userInfo[0][8] ? userInfo[0][8] : 0);
    }
  }, [userInfo]);

  //update info in database on last login time, after we've already queried so we can update new row status
  if (queryResult && userInfo && todoResult && companyResult) {
    const uid = userInfo[0][0];
    ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);
    ReactGA.set({
      userId: uid,
    });

    ReactGA.pageview('dashboard');

    createKanbanData(queryResult, data['lanes'], real_login_time);
    createTodoData(todoResult, todo_data['lanes']);
    const _renderCard = props => {
      return <NewCardForm {...props} companies={companyResult} />;
    };

    const _renderTodo = props => {
      return <NewTodoForm {...props} companies={companyResult} />;
    };

    const _renderCardTile = props => {
      return (
        <CustomCard {...props} setNewOffer={setNewOffer} newOffer={newOffer} />
      );
    };

    const _renderCardTileToDo = props => {
      return <CustomCard {...props} table={'todo'} />;
    };

    const components = {
      Card: _renderCardTile,
      NewCardForm: _renderCard,
    };

    const todoComponents = {
      Card: _renderCardTileToDo,
      NewCardForm: _renderTodo,
    };

    var allCompanies = getAllCompaniesInTable(data);
    return (
      <div>
        {newOffer.offer && <Confetti recycle={confetti} numberOfPieces={200} />}
        <CssBaseline />
        <AppBar
          elevation={0}
          position="flex"
          className={clsx(classes.appBar, classes.appBarShift)}
        >
          <Navbar
            openSettings={handleOpenSettings}
            data={data}
            handleCompanyModalOpen={handleCompanyModalOpen}
            handleCompanyModalClose={handleCompanyModalClose}
            email={userInfo[0][7]}
            page={'dashboard'}
          />
        </AppBar>

        <main className={classes.content}>
          <BugsBanner token={token} />
          {/* {location ? <SimpleModal open={openSimple} close={handleCloseSimple} name={location.state.referral}/> : <div/>}  */}
          {allCompanies.length == 0 ? <TransitionAlerts /> : <div />}
          <Container maxWidth="inherit" className={classes.container}>
            <Grid
              container
              direction={isMobile ? 'column' : 'row'}
              justify={isMobile ? 'center' : 'flex-start'}
              alignItems="stretch"
              style={{ overflow: 'scroll' }}
            >
              <Grid item xs={isMobile ? 12 : 3} style={{ flexBasis: '0%' }}>
                {/* todo board */}
                <div
                  className={
                    isMobile ? classes.todoBoardMobile : classes.todoBoard
                  }
                >
                  <Board
                    data={todo_data}
                    style={{
                      backgroundColor: '#f0f1f3',
                      fontFamily: 'Lato',
                      height: isMobile ? 'auto' : '',
                    }}
                    laneStyle={{ backgroundColor: '#efefef', width: 15 }}
                    components={todoComponents}
                    editable
                    onCardAdd={handleTodoAdd}
                    onCardDelete={handleTodoDelete}
                  />
                </div>
              </Grid>
              <Grid item xs={isMobile ? 12 : 9}>
                {/* companies dashboard */}
                <div
                  className={
                    isMobile
                      ? classes.companiesBoardMobile
                      : classes.companiesBoard
                  }
                >
                  <Board
                    data={data}
                    style={{
                      backgroundColor: '#f0f1f3',
                      fontFamily: 'Lato',
                      paddingLeft: '15',
                    }}
                    laneStyle={{ backgroundColor: '#efefef', width: 15 }}
                    components={components}
                    draggable
                    editable
                    onCardAdd={handleCardAdd}
                    onCardDelete={handleCardDelete}
                    onCardMoveAcrossLanes={handleCardMoveChangeStage}
                    onCardClick={handleCardClick}
                    onCardUpdate={handleCardUpdate}
                  />
                </div>
              </Grid>
            </Grid>
            <Box
              pt={4}
              justifyContent="center"
              display="flex"
              alignItems="center"
              flexDirection="column"
            >
              <Copyright />
            </Box>
            <Box
              pt={2}
              justifyContent="flex-end"
              display="flex"
              alignItems="flex-end"
              flexDirection="flex-end"
            ></Box>
          </Container>
        </main>
        {/* popup for new company */}
        <CustomizedDialogs info={openInfo} close={handleCloseInfo} />
        {/* popup for duplicate company */}
        <DuplicateCustomizedDialogs
          info={openDuplicateInfo}
          close={handleCloseDuplicateInfo}
        />
        <SimpleDialog
          open={openSettings}
          onClose={handleCloseSettings}
          token={token}
        />
        {companyModal && (
          <CompanyModal
            userInfo={userInfo}
            open={companyModal}
            onClose={handleCompanyModalClose}
            card={cardInfo}
            token={props.token}
            logo={filterByCID(companyResult, cardInfo.cid)}
            page="dashboard"
            isPipeline
            setRedemptionPoints={setRedemptionPoints}
            redemptionPoints={redemptionPoints}
          />
        )}
        <AlertDialog
          card={cardToDelete}
          open={deleteOpen}
          onClick={handleDeleteClickOpen}
          handleClose={handleDeleteClose}
          handleCloseCancel={handleDeleteCloseCancel}
        />
        <SimpleModal
          open={openSimple}
          handleClose={handleCloseSimple}
          name={name}
        />
      </div>
    );
  } else if (
    !!queryResult &&
    queryResult.length > 0 &&
    queryResult[0][pipToIndex.user_email] == null
  ) {
    delete_cookie('userToken');
    return (
      <Redirect
        push
        to={{
          pathname: '/',
        }}
      />
    );
  } else {
    return null;
  }
}
