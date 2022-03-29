import React from 'react';
import ReactGA from 'react-ga';
import AnimationRevealPage from '../../helpers/AnimationRevealPage';
import Hero from './Hero';
import Features from './Features';
import FAQ from './FAQ';
import Footer from './Footer';

export default function LandingPage(props) {
  ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);
  ReactGA.pageview('landing_page');
  return (
    <AnimationRevealPage>
      <Hero {...props} />
      <Features />
      <FAQ />
      <Footer />
    </AnimationRevealPage>
  );
}
