import React from 'react';

const VideoDownloadComponent = (props) => (
    props.isDownloadReady ? <div>
        <button onClick={props.onDownload}> Download Edited Video!</button>
    </div> : null
)

export default VideoDownloadComponent;