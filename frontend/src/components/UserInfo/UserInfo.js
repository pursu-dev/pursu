import React from 'react';
import ReactGA from 'react-ga';
import { Alert, AlertTitle, Autocomplete } from '@material-ui/lab';
import {
  CssBaseline,
  TextField,
  FormControlLabel,
  Checkbox,
  Box,
  makeStyles,
  Container,
} from '@material-ui/core';

import { Container as ContainerBase } from '../misc/Layouts';
import { ReactComponent as LoginIcon } from 'feather-icons/dist/icons/log-in.svg';
import { Redirect } from 'react-router-dom';
import AnimationRevealPage from '../../helpers/AnimationRevealPage.js';
import tw from 'twin.macro';
import styled from 'styled-components';
import illustration from '../../images/login-illustration.svg';
import logo from '../../images/Pursu_Truena_Small.png';
import vars from './Dropdowns.js';
import Copyright from '../misc/Copyright';
import { bake_cookie } from 'sfcookies';

function titleCase(str) {
  return str
    .split(' ')
    .map(item => item.charAt(0).toUpperCase() + item.slice(1).toLowerCase())
    .join(' ');
}

const ContainerOuter = tw(
  ContainerBase
)`min-h-screen bg-primary-900 text-white font-medium flex justify-center -m-8`;
const Content = tw.div`max-w-screen-xl m-0 sm:mx-20 sm:my-16 bg-white text-gray-900 shadow sm:rounded-lg flex justify-center flex-1`;
const MainContainer = tw.div`lg:w-1/2 xl:w-5/12 p-6 sm:p-12`;
const LogoLink = tw.a``;
const LogoImage = tw.img`h-12 mx-auto`;
const MainContent = tw.div`mt-12 flex flex-col items-center`;
const Heading = tw.h1`text-2xl xl:text-3xl font-extrabold`;
const FormContainer = tw.div`w-full flex-1 mt-8`;

const SubmitButton = styled.button`
  ${tw`mt-5 tracking-wide font-semibold bg-primary-500 text-gray-100 w-full py-4 rounded-lg hover:bg-primary-900 transition-all duration-300 ease-in-out flex items-center justify-center focus:shadow-outline focus:outline-none`}
  .icon {
    ${tw`w-6 h-6 -ml-2`}
  }
  .text {
    ${tw`ml-3`}
  }
`;
const IllustrationContainer = tw.div`sm:rounded-r-lg flex-1 bg-purple-100 text-center hidden lg:flex justify-center`;
const IllustrationImage = styled.div`
  ${props => `background-image: url("${props.imageSrc}");`}
  ${tw`m-12 xl:m-16 w-full max-w-sm bg-contain bg-center bg-no-repeat`}
`;

const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

const logoLinkUrl = '#';
const illustrationImageSrc = illustration;
const headingText = 'Sign Up For Pursu!';
const submitButtonText = 'Sign Up';
const SubmitButtonIcon = LoginIcon;

const genderMap = {
  '': '',
  Female: 1,
  Male: 0,
  'Prefer not to say': 3,
  Unspecified: 2,
};

class UserInfo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      redirect: false,
      name: '',
      college: '',
      major: '',
      year: new Date().getFullYear().toString(),
      consent: false,
      privacy: false,
      gender: '',
      ethnicity: '',
      alert: false,
      refName: '',
    };
    this.handleOnClick = this.handleOnClick.bind(this);
    this.handleOnChange = this.handleOnChange.bind(this);
    this.validate = this.validate.bind(this);
  }

  handleOnClick = () => {
    const validData = this.validate();
    if (validData !== true) {
      this.setState({
        alert: true,
        errorMessage: validData,
      });
      return;
    } else {
      this.setState({
        alert: false,
        errorMessage: '',
      });
    }
    let data = {
      name: this.state.name,
      college: this.state.college,
      year: this.state.year,
      major: this.state.major,
      consent: this.state.consent,
      gender: genderMap[this.state.gender],
      ethnicity: this.state.ethnicity,
      token: this.props.token,
      referral: this.props.referral,
    };
    let url = process.env.REACT_APP_USER_INFO;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }).then(response => {
      let ref_name = '';
      response.json().then(data => {
        ref_name = 'ref_name' in data ? data['ref_name'] : '';
        if (response.status === 200) {
          bake_cookie('userToken', [data['token'].replace(/^"|"$/g, '')]);
          if (this.props.referral) {
            localStorage.setItem('showReferralModal', true);
            this.setState({ redirect: true, alert: false, refName: ref_name });
          } else {
            this.setState({ redirect: true, alert: false });
          }
        } else {
          this.setState({
            alert: false,
            errorMessage: 'An error occurred. Please try again!',
          });
        }
      });
    });
  };

  handleOnChange = (e, value) => {
    let name = e.target.name;
    let id = e.target.id;
    if (id.includes('gender')) {
      this.setState({ gender: value });
    } else if (id.includes('major')) {
      this.setState({ major: value });
    } else if (id.includes('college')) {
      this.setState({ college: value });
    } else if (id.includes('ethnicity')) {
      this.setState({ ethnicity: value });
    }

    switch (name) {
      case 'name':
        this.setState({ name: e.target.value });
        break;
      case 'year':
        this.setState({ year: e.target.value });
        break;
      case 'consent':
        this.setState({ consent: e.target.checked });
        break;
      case 'privacy':
        this.setState({ privacy: e.target.checked });
        break;
    }
  };

  validate = () => {
    let errorString = 'Please fill in these fields:';
    let data = {
      name: this.state.name,
      college: this.state.college,
      year: this.state.year,
      major: this.state.major,
      privacy: this.state.privacy,
      gender: this.state.gender,
      ethnicity: this.state.ethnicity,
    };

    for (let key in data) {
      if (key === 'privacy' && !data['privacy']) {
        return "Please accept Pursu's privacy policy.";
      } else if (data[key] === '' || data[key] === null) {
        errorString += ' ' + key + ', ';
      }
    }

    if (errorString === 'Please fill in these fields:') {
      return true;
    }

    return errorString.slice(0, -2);
  };

  render() {
    if (this.state.redirect) {
      return (
        <Redirect
          push
          to={{
            pathname: '/dashboard',
            state: {
              userToken: this.props.token,
              referral: this.state.refName,
            },
          }}
        />
      );
    }
    ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);
    ReactGA.pageview('user_info');
    return (
      <div>
        <AnimationRevealPage>
          <ContainerOuter>
            <Content>
              <MainContainer>
                <LogoLink href={logoLinkUrl}>
                  <LogoImage src={logo} />
                </LogoLink>
                <MainContent>
                  <Heading>{headingText}</Heading>
                  <FormContainer>
                    <Container component="main" maxWidth="xs">
                      {this.state.alert && (
                        <Alert severity="error">
                          <AlertTitle>Error</AlertTitle>
                          {this.state.errorMessage}
                        </Alert>
                      )}
                      <CssBaseline />
                      <div className={useStyles.paper}>
                        <form className={useStyles.form} noValidate>
                          <TextField
                            variant="outlined"
                            margin="normal"
                            required
                            fullWidth
                            id="name"
                            label="Name"
                            name="name"
                            autoComplete="name"
                            value={this.state.name}
                            onChange={this.handleOnChange}
                          />
                          <Autocomplete
                            id="gender"
                            freeSolo
                            disableClearable
                            options={vars.genders.map(gender => gender)}
                            renderInput={params => (
                              <TextField
                                {...params}
                                label="Gender"
                                required
                                margin="normal"
                                variant="outlined"
                              />
                            )}
                            name="gender"
                            onChange={this.handleOnChange}
                          />
                          <Autocomplete
                            id="ethnicity"
                            freeSolo
                            disableClearable
                            options={vars.ethnicities.map(
                              ethnicity => ethnicity
                            )}
                            renderInput={params => (
                              <TextField
                                {...params}
                                label="Ethnicity"
                                required
                                margin="normal"
                                variant="outlined"
                              />
                            )}
                            name="ethnicity"
                            onChange={this.handleOnChange}
                          />
                          <Autocomplete
                            id="college"
                            freeSolo
                            disableClearable
                            options={vars.colleges.map(college => college)}
                            renderInput={params => (
                              <TextField
                                {...params}
                                label="College"
                                required
                                margin="normal"
                                variant="outlined"
                              />
                            )}
                            name="college"
                            onChange={this.handleOnChange}
                          />
                          <Autocomplete
                            id="major"
                            freeSolo
                            disableClearable
                            options={vars.majors.map(major => titleCase(major))}
                            renderInput={params => (
                              <TextField
                                {...params}
                                label="Major"
                                required
                                margin="normal"
                                variant="outlined"
                              />
                            )}
                            name="major"
                            onChange={this.handleOnChange}
                          />
                          <TextField
                            variant="outlined"
                            margin="normal"
                            required
                            fullWidth
                            id="year"
                            label="Graduation Year"
                            name="year"
                            autoComplete="year"
                            value={this.state.year}
                            type="number"
                            onChange={this.handleOnChange}
                          />
                          <br></br>
                          <FormControlLabel
                            control={
                              <Checkbox
                                required={true}
                                value="privacy"
                                color="primary"
                                checked={this.state.privacy}
                                onChange={this.handleOnChange}
                              />
                            }
                            name="privacy"
                            label={
                              <label>
                                I agree to{' '}
                                <a
                                  style={{ color: 'blue' }}
                                  href="https://bit.ly/32yM3Rv"
                                  target="_blank"
                                >
                                  Pursu's privacy policy
                                </a>{' '}
                                *
                              </label>
                            }
                          />
                          <FormControlLabel
                            control={
                              <Checkbox
                                value="consent"
                                color="primary"
                                checked={this.state.consent}
                                onChange={this.handleOnChange}
                              />
                            }
                            name="consent"
                            label="I consent to Pursu using my anonymous data to improve its service."
                          />
                        </form>
                        <SubmitButton
                          type="submit"
                          onClick={this.handleOnClick}
                        >
                          <SubmitButtonIcon className="icon" />
                          <span className="text">{submitButtonText}</span>
                        </SubmitButton>
                      </div>
                      <Box mt={8}>
                        <Copyright />
                      </Box>
                    </Container>
                  </FormContainer>
                </MainContent>
              </MainContainer>
              <IllustrationContainer>
                <IllustrationImage imageSrc={illustrationImageSrc} />
              </IllustrationContainer>
            </Content>
          </ContainerOuter>
        </AnimationRevealPage>
      </div>
    );
  }
}

export default UserInfo;
