// @flow

import React from 'react';
import {
  Button,
  RadioButtonGroup,
  RadioButton,
} from '@asidatascience/adler-ui';

import {
  submitSourceBias,
} from '../../api';

import './Source.css';

type Props = {
  nextSource: Function,
  source: {
    sourceId: string,
    name: string,
    description: string,
    url: string,
    languageCode: string,
    countryCode: string,
  },
};

type State = {
  politicalBias: null | 0 | 1 | 2,
  reliability: null | 0 | 1,
};

const positionToBias = [ 'left', 'center', 'right' ];
const postionToReliability = [ 'reliable', 'unreliable' ];

export default class Source extends React.Component<Props, State> {
  props: Props;
  state: State = {
    politicalBias: null,
    reliability: null,
  };
  
  handleSubmit = async () => {
    const { nextSource, source: { sourceId }} = this.props;
    const { politicalBias, reliability } = this.state;
    if (politicalBias && reliability) {
      submitSourceBias(sourceId, politicalBias, reliability);
      nextSource();
    }
  }
  
  handleSkip = () => {
    this.props.nextSource();
  }
  
  handlePoliticalBiasChange = (idx: number) => {
    this.setState({ politicalBias: idx });
  }
  
  handleReliabilityChange = (idx: number) => {
    this.setState({ reliability: idx });
  }
  
  render () {
    const {
      nextSource,
      source: {
        sourceId,
        name,
        description,
        url,
      },
    } = this.props;
    const { politicalBias, reliability } = this.state;

    return (
      <div className="Source" key={sourceId} >
        <div className="Source__favicon" >
          <img
            src={`https://plus.google.com/_/favicon?domain_url=${url}`}
            target="_blank"
            width="50px"
            height="50px"
          />
        </div>
        <div className="Source__name" >
          <a href={url}>{name}</a>
        </div>
        <div className="Source__description" >
          {description}
        </div>
        <div className="Source__politicalBias" >
          <RadioButtonGroup
            onChange={this.handlePoliticalBiasChange}
            horizontal
          >
            <RadioButton label="Left" />
            <RadioButton label="Center" />
            <RadioButton label="Right" />
          </RadioButtonGroup>
        </div>
        <div className="Source__reliabilty" >
          <RadioButtonGroup
            onChange={this.handleReliabilityChange}
            horizontal
          >
            <RadioButton label="Reliable" />
            <RadioButton label="Unreliable" />
          </RadioButtonGroup>
        </div>
        <div className="Source__buttons" >
          <Button
            text="Skip"
            onClick={this.handleSkip}
          />
          <Button
            text="Submit"
            disabled={politicalBias === null || reliability === null}
            onClick={this.handleSubmit}
          />
        </div>
      </div>
    );
  }
}
