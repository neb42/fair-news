// @flow

import React from 'react';

import { getSourceList } from '../../api';
import Source from '../Source';

import './App.css';

type State = {
  sourceIdx: number,
  sources: Array<{
    source_id: string,
    name: string,
    description: string,
    url: string,
    language_code: string,
    country_code: string,
  }>,
};

export default class App extends React.Component<*, State> {
  state: State = {
    sourceIdx: 0,
    sources: [],
  };
  
  async componentDidMount() {
    const sources = await getSourceList();
    this.setState({ sources });
  }
  
  handleNextSource = () => {
    this.setState(prevState => ({ sourceIdx: prevState.sourceIdx + 1 }));
  }
  
  render() {
    const { sources, sourceIdx } = this.state;
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">
            News Source Bias and Reliability Classifier
          </h1>
        </header>
        {sources.length > sourceIdx ? (
          <Source
            source={sources[sourceIdx]}
            nextSource={this.handleNextSource}
          />
        ) : <div />}
      </div>
    );
  }
}
