import React from 'react';

const VideoUploadComponent = (props) => (
    <div>
        <h2>
            Video Upload:
        </h2>
        <input type='file' onChange={props.onVideoUpload}></input>
    </div>
)

export default VideoUploadComponent;