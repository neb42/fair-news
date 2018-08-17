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
    source_id: string,
    name: string,
    description: string,
    url: string,
    language_code: string,
    country_code: string,
  },
};

type State = {
  politicalBias: null | 0 | 1 | 2,
  reliability: null | 0 | 1,
};

export default class Source extends React.Component<Props, State> {
  props: Props;
  state: State = {
    politicalBias: null,
    reliability: null,
  };
  
  handleSubmit = async () => {
    const { nextSource, source: { source_id }} = this.props;
    const { politicalBias, reliability } = this.props;
    if (politicalBias && reliability) {
      submitSourceBias();
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
        name,
        description,
        url,
      },
    } = this.props;
    const { politicalBias, reliability } = this.state;

    return (
      <div className="Source" >
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
