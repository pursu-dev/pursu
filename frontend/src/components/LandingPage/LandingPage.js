import React from 'react';
import ReactGA from 'react-ga';
import Hero from './Hero';
import Features from './Features';
import ExploreFeatures from './ExploreFeatures';
import FAQ from './FAQ';
import Footer from './Footer';
import MobileLandingPage from '../MobileLandingPage/LandingPage';
import { isMobile } from 'react-device-detect';

export default function LandingPage(props) {
  ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);
  ReactGA.pageview('landing_page');
  if (isMobile) {
    return <MobileLandingPage />;
  } else {
    return (
      <div>
        <Hero {...props} />
        <Features />
        <ExploreFeatures />
        <FAQ />
        <Footer />
      </div>
    );
  }
}
