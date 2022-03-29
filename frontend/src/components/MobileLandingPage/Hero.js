import React from 'react';
import PopUp from './PopUp.js';
import styled from 'styled-components';
import tw from 'twin.macro';
import Header from './Header.js';
import { ReactComponent as SvgDecoratorBlob1 } from '../../images/svg-decorator-blob-1.svg';
import DesignIllustration from '../../images/undraw_interview_rmcf.svg';
import SchoolsLogoStripImage from '../../images/oldschools.png';
import { Alert, AlertTitle } from '@material-ui/lab';
import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const Container = tw.div`relative`;
const AlertContainer = tw.div`flex flex-col max-w-screen-xl mx-auto mt-5`;
const TwoColumn = tw.div`flex flex-col lg:flex-row lg:items-center max-w-screen-xl mx-auto py-20 md:py-24`;
const LeftColumn = tw.div`relative lg:w-5/12 text-center max-w-lg mx-auto lg:max-w-none lg:text-left`;
const RightColumn = tw.div`relative mt-12 lg:mt-0 flex-1 flex flex-col justify-center lg:self-end`;

const Heading = tw.h1`font-bold text-3xl md:text-3xl lg:text-4xl xl:text-5xl text-gray-900 leading-tight`;
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
function roundedHeaderButton(props) {
  return (
    <>
      <Header
        func={props.func}
        roundedHeaderButton={roundedHeaderButton}
        failure={props.failure}
        setClientID={props.setClientID}
      />
      <Container>
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
        <TwoColumn>
          <LeftColumn>
            <Heading>
              <span tw="text-primary-700">Automate</span> your recruiting
              process.
            </Heading>
            <Paragraph>
              Pursu enables you to collect, organize, and optimize your
              recruiting information so you can focus on nailing the interview.
            </Paragraph>
            <PopUp
              func={props.func}
              failure={props.failure}
              setClientID={props.setClientID}
              message={'Continue'}
            />
            <CustomersLogoStrip>
              <p>trusted by students from</p>
              <img src={SchoolsLogoStripImage} alt="Our Customers" />
            </CustomersLogoStrip>
          </LeftColumn>
          <RightColumn>
            <IllustrationContainer>
              <img
                tw="min-w-0 w-full max-w-lg xl:max-w-3xl"
                src={DesignIllustration}
                alt="Design Illustration"
              />
            </IllustrationContainer>
          </RightColumn>
        </TwoColumn>
        <DecoratorBlob1 />
      </Container>
    </>
  );
}
export default roundedHeaderButton;
