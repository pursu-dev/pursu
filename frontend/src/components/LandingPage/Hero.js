import React from 'react';
import PopUp from './PopUp.js';
import styled from 'styled-components';
import tw from 'twin.macro';
import Header from './Header.js';
import { ReactComponent as SvgDecoratorBlob1 } from '../../images/svg-decorator-blob-1.svg';
import SchoolsLogoStripImage from '../../images/schools.png';
import { Alert, AlertTitle } from '@material-ui/lab';
import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { registerables } from 'chart.js';
import ToolbarComponent from '../Shared/Toolbar.js';

const emoji = require('emoji-dictionary');

const useStyles = makeStyles({
  emoji: {
    width: '50px',
    height: '50px',
    background: 'rgba(255, 255, 255, 0.25)',
    borderRadius: '25px',
    display: 'flex',
    justifyContent: 'center',
    padding: '15px 0',
    marginBottom: '7px',
  },
  emojiSize: {
    lineHeight: '0.8em',
    fontSize: '1.5em',
  },
  hero: {
    backgroundColor: 'rgba(119, 54, 207, 0.8)',
    zIndex: '1',
    fontFamily: 'Poppins',
    paddingTop: '50px',
    color: 'white',
  },
  headerContainer: {
    width: '50%',
    flexWrap: 'wrap',
  },
  mainContainer: {
    zIndex: '2',
  },
  heroBody: {
    padding: '60px',
    objectFit: 'contain',
  },
  heroText: {
    color: 'white',
    zIndex: '1',
    fontWeight: 'bolder',
  },
  activeButton: {
    backgroundColor: '#B49BD4',
    color: 'white',
    zIndex: '1',
  },
  mainInfo: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'left',
    marginBottom: '10vh',
    flexWrap: 'wrap',
    color: 'white',
    zIndex: '1',
    fontFamily: 'Lato',
    paddingTop: '50px',
  },
  infoWidget: {
    width: '230px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'left',
    marginRight: '50px',
    zIndex: '1',
  },
  laptopGraphic: {
    position: 'absolute',
    left: '0px',
    top: '0px',
    float: 'right',
    zIndex: '-1',
    width: '100%',
    height: 'auto',
    objectFit: 'contain',
  },
  laptopContainer: {
    // display: 'flex',
    zIndex: '1',
    objectFit: 'contain',
  },
  schoolContainer: {
    marginTop: '10px',
    width: '500px',
    height: 'auto',
    objectFit: 'contain',
  },
  schoolsGraphic: {
    width: '100%',
    height: 'auto',
    backgroundImage: 'url()',
  },
});

const Container = tw.div`relative`;
const AlertContainer = tw.div`flex flex-col max-w-screen-xl mx-auto mt-5`;
const TwoColumn = tw.div`flex flex-col lg:flex-row lg:items-center max-w-screen-xl mx-auto py-20 md:py-24`;
// const LeftColumn = tw.div`relative lg:w-5/12 text-center max-w-lg mx-auto lg:max-w-none lg:text-left`;
const LeftColumn = tw.div`relative text-center max-w-lg mx-auto lg:max-w-none lg:text-left`;
const RightColumn = tw.div`relative mt-12 lg:mt-0 flex-1 flex flex-col justify-center lg:self-end`;
// const Heading = tw.h1`font-bold text-6xl`;
const Heading = tw.h1`font-bold text-6xl sm:text-4xl md:text-6xl lg:text-6xl xl:text-6xl leading-tight`;
const Paragraph = tw.p`my-5 lg:my-8 text-base xl:text-lg`;

const IllustrationContainer = tw.div`flex justify-center lg:justify-end items-center`;

// Random Decorator Blobs (shapes that you see in background)
const DecoratorBlob1 = styled(SvgDecoratorBlob1)`
  ${tw`pointer-events-none opacity-5 absolute left-0 bottom-0 h-64 w-64 transform -translate-x-2/3 -z-10`}
`;

const CustomersLogoStrip = styled.div`
  ${tw`mt-12 lg:mt-20`}
  p {
    ${tw`text-sm lg:text-sm tracking-wider font-bold`}
  }
  img {
    ${tw`mt-1 w-full lg:pr-16 xl:pr-32`}
  }
`;

// export default ({ roundedHeaderButton }) => {
function RoundedHeaderButton(props) {
  const classes = useStyles();
  return (
    <div className={classes.hero}>
      <Header
        func={props.func}
        roundedHeaderButton={RoundedHeaderButton}
        failure={props.failure}
        setClientID={props.setClientID}
      />
      <Container className={classes.mainContainer}>
        {props.alert && (
          <AlertContainer>
            <Alert classes={{ fontSize: 'large' }} severity="error">
              <Typography>
                Looks like you signed up without granting us all requested Gmail
                permissions. For Pursu to do its magic, try signing up again
                with permissions enabled! Please feel free to review our{' '}
                <a
                  style={{ color: 'blue' }}
                  href="https://bit.ly/32yM3Rv"
                  target="_blank"
                >
                  Privacy Policy
                </a>{' '}
                if you have any questions.
              </Typography>
            </Alert>
          </AlertContainer>
        )}
        <div className={classes.heroBody}>
          <div className={classes.headerContainer}>
            <Heading className={classes.heroText}>
              Automate your recruiting process.
            </Heading>
          </div>
          <div className={classes.mainInfo}>
            <div className={classes.infoWidget}>
              <div className={classes.emoji}>
                <div className={classes.emojiSize}>
                  {emoji.getUnicode('robot')}
                </div>
              </div>
              <div>
                Automate the organizational parts of recruiting and discover new
                job opportunities
              </div>
            </div>
            <div className={classes.infoWidget}>
              <div className={classes.emoji}>
                {' '}
                <div className={classes.emojiSize}>
                  {emoji.getUnicode('dart')}
                </div>
              </div>
              <div>Focus your time on nailing the interview</div>
            </div>
            <div className={classes.infoWidget}>
              <div className={classes.emoji}>
                {' '}
                <div className={classes.emojiSize}>
                  {emoji.getUnicode('wave')}
                </div>
              </div>
              <div>Unlock access to recruiters at top companies</div>
            </div>
            <div className={classes.infoWidget}>
              <div className={classes.emoji}>
                {' '}
                <div className={classes.emojiSize}>
                  {emoji.getUnicode('eyes')}
                </div>
              </div>
              <div>
                See anonymous insights on how your classmates are recruiting
              </div>
            </div>
            {/* <div className={classes.laptopContainer}>
              <img
                className={classes.laptopGraphic}
                src={DesignIllustration}
                alt="Design Illustration"
              />
            </div> */}
          </div>
          <PopUp
            func={props.func}
            failure={props.failure}
            setClientID={props.setClientID}
            message={'Continue'}
          />
          <CustomersLogoStrip>
            <p>trusted by students from</p>
            <div className={classes.schoolContainer}>
              <img
                className={classes.schoolsGraphic}
                src={SchoolsLogoStripImage}
                alt="Our Customers"
              />
            </div>
          </CustomersLogoStrip>
        </div>
        <DecoratorBlob1 />
      </Container>
      {/* <div className={classes.laptopContainer}>
        <img
          className={classes.laptopGraphic}
          src={DesignIllustration}
          alt="Design Illustration"
        />
      </div> */}
    </div>
  );
}
export default RoundedHeaderButton;
