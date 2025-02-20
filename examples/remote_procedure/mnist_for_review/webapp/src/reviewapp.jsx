/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { BaseFrontend } from "./components/core_components.jsx";

function ReviewApp() {
  const appRef = React.useRef(null);
  const [reviewData, setReviewData] = React.useState(null);

  // Requirement #1. Render review components after receiving Task data via message
  window.onmessage = function (e) {
    const data = JSON.parse(e.data);
    setReviewData(data["REVIEW_DATA"]);
  };

  // Requirement #2. Resize iframe height to fit its content
  React.useLayoutEffect(() => {
    function updateSize() {
      if (appRef.current) {
        window.top.postMessage(
          JSON.stringify({
            IFRAME_DATA: {
              height: appRef.current.offsetHeight,
            },
          }),
          "*"
        );
      }
    }
    window.addEventListener("resize", updateSize);
    updateSize();
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  // Requirement #3. This component must return a div with `ref={appRef}`
  // so we can get displayed height of this component (for iframe resizing)
  return (
    <div ref={appRef}>
      {reviewData ? (
        <BaseFrontend
          initialTaskData={reviewData["inputs"]}
          finalResults={reviewData["outputs"]}
        />
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}

ReactDOM.render(<ReviewApp />, document.getElementById("app"));
