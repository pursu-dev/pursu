import React, { useState, useEffect, useRef } from 'react';
import { Bar, defaults, Chart } from 'react-chartjs-2';
import { Box, makeStyles, Typography } from '@material-ui/core';
import 'chart.js/helpers';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { isMobile } from 'react-device-detect';

const useStyles = makeStyles({
  title: {
    fontSize: '24px',
    fontFamily: 'Poppins',
    fontWeight: 500,
    marginBottom: '10px',
  },
  text: {
    fontFamily: 'Poppins',
    fontWeight: 400,
    fontSize: '20px',
  },
});

const convertInsight = dataPoint => {
  if (dataPoint === 0) {
    return 0;
  }
  // split by hyphen
  const splitData = dataPoint.split('-');
  const month = parseInt(splitData[0]);
  const day = parseInt(splitData[1]);

  const conversion = (((month + 6) % 12) * 30 + day) % 365; // 151 is offset from jun
  return conversion;
};

export default function InsightsGraph(props) {
  const classes = useStyles();
  const ref = useRef();
  defaults.font.family = 'Poppins';
  defaults.font.weight = '500';
  Chart.register(ChartDataLabels);
  const [chartData, setChartData] = React.useState(null);

  useEffect(() => {
    if (props.isDemo) {
      setChartData([
        [0, 48],
        [50, 100],
        [80, 140],
        [120, 180],
      ]);
      return;
    }

    const sorted = [...props.insightsData].sort((left, right) => {
      if (left[0] < right[0]) {
        return -1;
      }
      if (left[0] > right[0]) {
        return 1;
      }
      return 0;
    });

    // app, cod, int, off
    // 0, 2, 3, 5
    const insightsTimes = [
      [0, 0],
      [0, 0],
      [0, 0],
      [0, 0],
    ];

    for (let i = 0; i < sorted.length; i++) {
      if (sorted[i][0] === 0) {
        // application
        insightsTimes[0][0] = sorted[i][2];
        insightsTimes[0][1] = sorted[i][3];
      }
      if (sorted[i][0] === 2) {
        // coding challenge
        insightsTimes[1][0] = sorted[i][2];
        insightsTimes[1][1] = sorted[i][3];
      }
      if (sorted[i][0] === 3) {
        // interview
        insightsTimes[2][0] = sorted[i][2];
        insightsTimes[2][1] = sorted[i][3];
      }
      if (sorted[i][0] === 5) {
        // offer
        insightsTimes[3][0] = sorted[i][2];
        insightsTimes[3][1] = sorted[i][3];
      }
    }

    const convertedIntegers = [
      [0, 0],
      [0, 0],
      [0, 0],
      [0, 0],
    ];

    for (let i = 0; i < insightsTimes.length; i++) {
      for (let j = 0; j < insightsTimes[i].length; ++j) {
        convertedIntegers[i][j] = convertInsight(insightsTimes[i][j]);
      }
    }

    setChartData(convertedIntegers);
  }, [props.insightsData]);

  const data = {
    labels: ['App', 'Coding', 'Interview', 'Offer'],
    datasets: [
      {
        data:
          !!props.insightsData && props.insightsData.length === 0
            ? [
                [0, 48],
                [50, 100],
                [80, 140],
              ]
            : chartData,
        backgroundColor: ['#B3B6DE', '#737C93', '#5B5B5B', '#6769C5'],
        borderWidth: 0,
        borderRadius: 100,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    elements: {
      bar: {
        borderWidth: 2,
      },
    },
    responsive: true,
    plugins: {
      datalabels: {
        formatter: function(value, context) {
          return context.chart.data.labels[context.dataIndex];
        },
        color: 'white',
        font: {
          weight: 'bold',
        },
      },
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        enabled: true,
        xAlign: 'left',
        yAlign: 'center',
        callbacks: {
          label: function(context) {
            return '';
          },
        },
      },
    },
    scales: {
      x: {
        position: 'top', // `axis` is determined by the position as `'y'`
        grid: {
          offset: true,
        },
        ticks: {
          stepSize: 30,
          callback: function(value, index, values) {
            const labels = [
              'JUN',
              'JUL',
              'AUG',
              'SEP',
              'OCT',
              'NOV',
              'DEC',
              'JAN',
              'FEB',
              'MAR',
              'APR',
              'MAY',
            ];
            const labelIndex = Math.floor(value / 30);
            return labels[labelIndex];
          },
        },
      },
      y: {
        position: 'right', // `axis` is determined by the position as `'y'`
        reverse: false,
        grid: {
          lineWidth: 0,
        },
        ticks: {
          display: false,
          mirror: true,
          padding: -3,
        },
      },
    },
  };

  return (
    <Box className={props.classes.insightsGraph}>
      <Typography variant="h5" className={classes.title}>
        {!!props.insightsData && props.insightsData.length === 0
          ? 'Collecting Timeline Data'
          : 'Recruiting Timeline'}
      </Typography>

      <Bar
        style={
          !!props.insightsData && props.insightsData.length === 0
            ? { filter: 'blur(5px)' }
            : {}
        }
        ref={ref}
        data={data}
        width={isMobile ? 320 : 400}
        height={isMobile ? 260 : 300}
        options={options}
      />
    </Box>
  );
}
