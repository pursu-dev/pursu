import React, { useEffect } from 'react';
import clsx from 'clsx';
import {
  makeStyles,
  CssBaseline,
  Box,
  AppBar,
  Container,
  Grid,
} from '@material-ui/core';
import CustomizedDialogs from '../Table/NewCompanyModal';
import DuplicateCustomizedDialogs from '../Table/DuplicateCompanyModal';
import Copyright from '../misc/Copyright';
import SimpleDialog from '../Dashboard/SimpleDialog';
import Board from 'react-trello';
import NewCardForm from '../Dashboard/CustomCard';
import NewTodoForm from '../Dashboard/TodoForm';
import CompanyModal from '../Shared/CompanyModal';
import CustomCard from '../Dashboard/CustomCardTile';
import Navbar from '../Shared/Navbar';
import AlertDialog from '../Dashboard/AlertDialog';
import TransitionAlerts from '../Dashboard/TransitionAlerts';
import Confetti from 'react-confetti';
import { isMobile } from 'react-device-detect';
import companyList from './companyList';
import { cloneDeep } from 'lodash';

const lookupLane = {
  lane0: 'Application',
  lane1: 'Referral',
  lane2: 'Coding Challenge',
  lane3: 'Interview',
  lane5: 'Offer',
  lane6: 'Rejection',
};

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

function createKanbanData(cardData) {
  return cloneDeep(cardData);
}

function createTodoData(todoData) {
  return cloneDeep(todoData);
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

export default function Demo(props) {
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
        cards: [
          {
            id: 'Card1',
            task: 'Create todo tasks to complete!',
            deadline: 'Deadlines will display here',
            draggable: true,
          },
          {
            id: 'Card2',
            task: 'Information will be lost on refresh',
            deadline: 'Sign up to save your board!',
            draggable: true,
          },
        ],
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
        cards: [
          {
            id: 'Card1',
            title: 'Pursu',
            recruiterName: 'Jane Doe',
            recruiterEmail: 'jane.doe@pursu.dev',
            description:
              'As you get recruiting emails, your dashboard will automatically populate!',
            draggable: true,
            link: 'https://hackerrank.com/challenges/fizzbuzz/problem/',
          },
          {
            id: 'Card2',
            title: 'Demo',
            recruiterName: 'Tech Nology',
            recruiterEmail: 'Tech.Nology@tech.org',
            description: 'You can also add your own custom cards!',
            draggable: true,
          },
        ],
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
        cards: [
          {
            id: 'Sents',
            title: 'Sents',
            description:
              'Click a card to see more information and insights! All data is mocked in the demo.',
            draggable: true,
            recruiterName: 'John Doe',
            recruiterEmail: 'john.doe@sents.dev',
            link:
              'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
          },
        ],
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

  const [cardData, setCardData] = React.useState(data);
  const [todoData, setTodoData] = React.useState(todo_data);
  const [deleteOpen, setDeleteOpen] = React.useState(false);
  const [cardToDelete, setCardToDelete] = React.useState(null);
  let eventBus = undefined;
  const setEventBus = handle => {
    eventBus = handle;
  };
  const handleDeleteClickOpen = () => {
    setDeleteOpen(true);
  };

  const handleDeleteCloseCancel = () => {
    setDeleteOpen(false);
  };

  const handleDeleteClose = (e, card) => {
    setDeleteOpen(false);
  };
  const [openInfo, setOpenInfo] = React.useState(false);
  const [openSettings, setOpenSettings] = React.useState(false);
  const [openDuplicateInfo, setDuplicateInfo] = React.useState(false);
  const [cardInfo, setCardInfo] = React.useState(null);
  const [newOffer, setNewOffer] = React.useState(false);
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
  const [update, setUpdate] = React.useState(false);
  const handleCompanyModalOpen = card => {
    setCardInfo(card);
    setUpdate(Math.random());
  };

  useEffect(() => {
    if (cardInfo !== null) {
      setCompanyModal(true);
    }
  }, [cardInfo, update]);

  useEffect(() => {
    if (newOffer === true) {
      setTimeout(() => setNewOffer(false), 10000);
      setTimeout(() => setConfetti(false), 5000);
    }
  }, [newOffer]);

  const handleCompanyModalClose = () => {
    setCompanyModal(false);
  };

  const handleCardAdd = (card, laneId) => {
    let company_name = card.title;
    let inTable = checkCurrentCompanies(cardData, company_name);
    if (inTable) {
      handleOpenDuplicateInfo();
      return;
    }
    const newCardData = { ...cardData };
    let lane = filterByTitle(newCardData.lanes, lookupLane[laneId]);
    let cards = lane['cards'];

    cards.push({
      id: card.id,
      title: company_name,
      description: card.description,
      recruiterName: 'San Francisco',
      recruiterEmail: 'SF@bayarea.com',
      draggable: true,
    });

    setCardData(newCardData);
  };

  const handleTodoAdd = (card, laneId) => {
    const newTodoData = { ...todoData };
    let cards = newTodoData.lanes[0]['cards'];

    cards.push(card);
    card.draggable = true;
    setTodoData(newTodoData);
  };

  const handleCardDelete = (cardId, laneId) => {
    const newCardData = { ...cardData };
    var finder = filterById(newCardData.lanes, laneId);
    let ind = 0;
    for (let i = 0; i < finder.cards.length; ++i) {
      if (finder.cards[i].id == cardId) {
        ind = i;
        break;
      }
    }
    finder.cards.splice(ind, 1); // deleting this cardId

    setCardData(newCardData);
  };

  const handleTodoDelete = (cardId, laneId) => {
    const newTodoData = { ...todoData };
    var finder = todoData.lanes[0];
    let ind = 0;
    for (let i = 0; i < finder.cards.length; ++i) {
      if (finder.cards[i].id == cardId) {
        ind = i;
        break;
      }
    }
    finder.cards.splice(ind, 1); // deleting this cardId
    setTodoData(newTodoData);
  };

  const handleCardMoveChangeStage = (fromLaneId, toLaneId, cardId, index) => {
    var fromLane = filterById(cardData.lanes, fromLaneId);
    var card = filterById(fromLane.cards, cardId);
    let company_name = card.title;

    const newCardData = { ...cardData };
    var finder = filterById(newCardData.lanes, fromLaneId);
    let ind = 0;
    for (let i = 0; i < finder.cards.length; ++i) {
      if (finder.cards[i].id == cardId) {
        ind = i;
        break;
      }
    }
    finder.cards.splice(ind, 1); // deleting this cardId
    let lane = filterByTitle(newCardData.lanes, lookupLane[toLaneId]);
    let cards = lane['cards'];
    let j = cards.length + 1;

    cards.push({
      id: card.id,
      title: company_name,
      description: card.description,
      draggable: true,
    });

    setCardData(newCardData);
    if (toLaneId === 'lane5') {
      setNewOffer(true);
      setConfetti(true);
    }
  };

  const handleCardClick = (cardId, metadata, laneId) => {
    let lane = filterById(cardData.lanes, laneId);
    let card = filterById(lane.cards, cardId);
    handleCompanyModalOpen(card);
    setUpdate(Math.random());
  };

  const handleCardUpdate = (laneId, cardId) => {};

  //components for queries
  let token = props.token;
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  const _renderCard = props => {
    return <NewCardForm {...props} companies={companyList} isDemo />;
  };

  const _renderTodo = props => {
    return <NewTodoForm {...props} companies={companyList} isDemo />;
  };

  const _renderCardTile = props => {
    return <CustomCard {...props} setNewOffer={setNewOffer} />;
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
    <div className={classes.root}>
      {newOffer && <Confetti recycle={confetti} numberOfPieces={200} />}
      <CssBaseline />
      <AppBar
        elevation={0}
        position="absolute"
        className={clsx(classes.appBar, open && classes.appBarShift)}
      >
        <Navbar
          openSettings={handleOpenSettings}
          data={cardData}
          handleCompanyModalOpen={handleCompanyModalOpen}
          handleCompanyModalClose={handleCompanyModalClose}
          page={'dashboard'}
          isDemo
        />
      </AppBar>

      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
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
                  data={createTodoData(todoData)}
                  style={{
                    backgroundColor: '#f0f1f3',
                    fontFamily: 'Lato',
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
                  data={createKanbanData(cardData)}
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
      <CompanyModal
        open={companyModal}
        onClose={handleCompanyModalClose}
        cid={cardInfo ? cardInfo.cid : 0}
        companyName={cardInfo ? cardInfo.title : ''}
        tab={'information'}
        card={cardInfo}
        token={props.token}
        isDemo
        isPipeline
      />
      <AlertDialog
        card={cardToDelete}
        open={deleteOpen}
        onClick={handleDeleteClickOpen}
        handleClose={handleDeleteClose}
        handleCloseCancel={handleDeleteCloseCancel}
      />
    </div>
  );
}
