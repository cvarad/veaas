import axios from 'axios';

import React, { Component } from 'react';
import { HeadingComponent, InputComponent, SubmitComponent, VideoDownloadComponent, VideoUploadComponent } from './components';

class App extends Component {
  state = {
    selectedFile: null,
    selectedOperations: {},
    hashAcknowledgement: '',
    isDownloadReady: false,
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

    axios.post("/apiv1/operation", formData)
      .then((response) => {
        this.setState({ hashAcknowledgement: response.data.hash })
        const eventSource = new EventSource("/apiv1/notification/" + response.data.hash)
        eventSource.onmessage = () => {
          this.setState({ isDownloadReady: true });
        };
      });

  };

  onDownload = () => {
    axios({
      url: "/apiv1/video/" + this.state.hashAcknowledgement,
      method: 'GET',
      responseType: 'blob'
    }).then((response) => {
      // create file link in browser's memory
      const href = URL.createObjectURL(response.data);

      // create "a" HTML element with href to file & click
      const link = document.createElement('a');
      link.href = href;
      link.setAttribute('download', 'output.mp4'); //or any other extension
      document.body.appendChild(link);
      link.click();

      // clean up "a" element & remove ObjectURL
      document.body.removeChild(link);
      URL.revokeObjectURL(href);
    });

  }

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
        <VideoDownloadComponent
          isDownloadReady={this.state.isDownloadReady}
          onDownload={this.onDownload}
        />
      </div>
    );
  }
}

export default App;