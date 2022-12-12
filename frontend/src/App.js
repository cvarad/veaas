import axios from 'axios';

import React, { Component } from 'react';
import { HeadingComponent, InputComponent, SubmitComponent, VideoUploadComponent } from './components';

class App extends Component {
  state = {
    selectedFile: null,
    selectedOperations: {},
  };

  onVideoUpload = event => {
    this.setState({ selectedFile: event.target.files[0] });
  };

  onInputChange = updatedSelectedOperations => {
    this.setState({ selectedOperations: updatedSelectedOperations })
  }

  onSubmitClick = () => {

    var formData = new FormData();

    formData.append(`file`, this.state.selectedFile);

    formData.append('operations',
      new Blob([JSON.stringify(this.state.selectedOperations)], {
        type: 'application/json'
      }));

    console.log(this.state.selectedOperations)

    axios.post("http://localhost:5000/apiv1/operation", formData);

  };

  render() {
    return (
      <div>
        <HeadingComponent />
        <VideoUploadComponent
          onVideoUpload={this.onVideoUpload}
        />
        <InputComponent
          onInputChange={this.onInputChange}
        />
        <SubmitComponent
          onSubmitClick={this.onSubmitClick}
        />
      </div>
    );
  }
}

export default App;