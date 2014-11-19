     var xhr = null, res = null, uploading = false;
      function done_zip() {
          document.getElementById('UploadFile_zip').value = "";
          setTimeout("document.getElementById('progress_zip').style.width = \"0%\"",1000);
          document.getElementById('UploadFileButton_zip').className = "btn btn-danger";
          document.getElementById('UploadFileButton_zip').innerHTML = "Abort";
          document.getElementById('UploadFileButton_zip').disabled = "disabled";
          alert(res['htm']);
          document.getElementById('DataConfig').value = res['SmartConfig']
      }
      
      function uploadFile_zip(e,url) {
        if (e) {
          e.stopPropagation();
          e.preventDefault();
        }
        if (document.getElementById('UploadFile_zip').files.length == 0) {
          alert('Empty File')
          return;
        }
        file = document.getElementById('UploadFile_zip').files[0]
        var ext = file.name.substring(file.name.lastIndexOf('.'), file.name.length);
        console.log(ext);
        if(ext !== '.zip') {
          alert("Must be zip");
          return;
        }
        if (!uploading) {
          document.getElementById('UploadFileButton_zip').innerHTML = "Abort";
          document.getElementById('UploadFileButton_zip').className = "btn btn-danger";
          document.getElementById('UploadFileButton_zip').disabled = "";
          uploading = true;
        }else {
          xhr.abort();
          return;
        }
    		var fd = new FormData();
     	 	fd.append("UploadFile", file);
     	 	fd.append("Status", "OK");
		    xhr = new XMLHttpRequest();
		    xhr.upload.addEventListener("progress", function(evt){
			    uploadProgress_zip(evt);
		    }, false);
		    xhr.onreadystatechange = function ( e ) {
            if ( xhr.readyState == 4 ) {
                if( xhr.status == 200 ) {
                    if (uploading) {
                        res = eval('('+e.target.responseText+')');
                        done_zip();
                    }
                } else {
                  alert('Abort or Failed');
                  document.getElementById('progress_zip').style.width = "0%";
                  document.getElementById('UploadFileButton_zip').className = "btn btn-primary";
                  document.getElementById('UploadFileButton_zip').innerHTML = "Reupload";
                  document.getElementById('UploadFileButton_zip').disabled = "";
                }
                uploading = false;
            }
        };
      	xhr.open("POST", url+'t'+document.getElementById('ProblemTime').value+'m'+document.getElementById('ProblemMemory').value);
      	xhr.send(fd);      	
      }
      

      function uploadProgress_zip(evt) {
        try {
          var percentComplete = Math.round(evt.loaded * 100 / evt.total);
          document.getElementById('progress_zip').style.width = percentComplete + "%";
          if (percentComplete == 100) {
              document.getElementById('UploadFileButton_zip').innerHTML = "Writing..";
              document.getElementById('UploadFileButton_zip').disabled = "disabled";
              document.getElementById('UploadFileButton_zip').className = "btn btn-success";
          }
        } catch(e) {
        	throw e;
        }
      }
      function writefile_zip(e){
          e.stopPropagation();
          e.preventDefault();
          document.getElementById('UploadFile_zip').files = e.dataTransfer.files;
          e.target.className = (e.type == "dragover" ? "hover" : "");
      }
      function config(id, url){
		      xh = new XMLHttpRequest();
		      xh.onreadystatechange = function ( e ) {
              if ( xh.readyState == 4 ) {
                  if( xh.status == 200 ) {
                    res = eval('('+e.target.responseText+')');
                    if (id == 0) document.getElementById('DataConfig').value = res['SmartConfig']
                    else if (id == 1) document.getElementById('DataConfig').value = res['DefaultConfig']
                    else document.getElementById('DataConfig').value = res['OriginalConfig']
                  }else alert('Config Failed');
              }
          };
		      xh.open("GET", url+'t'+document.getElementById('ProblemTime').value+'m'+document.getElementById('ProblemMemory').value);
		      xh.send();
      }
      
