     var xhr = null, res = null, uploading = false;
     function fileSelected(file) {
        var files = file.files, length = files.length, fid;
        if (length > 0) {
        	for(var i = 0; i < length; i++) {
		        if(files[i].type === 'image/jpeg' || files[i].type === 'image/png') {
		        	fid = new Date().getTime() + i.toString();
		        	buildPreviewImgList(files[i], fid, uploadFile);
		        } else{
		        	throw '类型错误，请上传png或jpg类型的图片';
		        }
        	}
        }
      }
      
      function done() {
          document.getElementById('UploadFile').value = "";
          setTimeout("document.getElementById('progress').style.width = \"0%\"",1000);
          setTimeout("$(\"#uploadimage-container\").prepend(res[\"htm\"]);",100);
          $("#defaultInput")[0].value = res["href"];
      }
      
      function uploadFile() {
        if (document.getElementById("UploadFile").files.length == 0) {
          alert('Empty File')
          return;
        }
        file = document.getElementById("UploadFile").files[0]
        if(file.type !== 'image/jpeg' && file.type !== 'image/png' && file.type !== 'image/gif') {
          alert("Must be in ['jpg', 'png', 'gif']");
          return;
        }
        if (!uploading) {
          document.getElementById('UploadFileButton').innerHTML = "Abort";
          document.getElementById('UploadFileButton').className = "btn btn-danger";
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
			    uploadProgress(evt);
		    }, false);
		    xhr.onreadystatechange = function ( e ) {
            if ( xhr.readyState == 4 ) {
                if( xhr.status == 200 ) {
                    if (uploading) {
                        res = eval('('+e.target.responseText+')');
                        done();
                    }
                } else alert('Abort or Failed');
                document.getElementById('UploadFileButton').className = "btn btn-primary";
                document.getElementById('UploadFileButton').innerHTML = "Submit";
                document.getElementById('UploadFileButton').disabled = "";
                uploading = false;
            }
        };
      	xhr.open("POST", "/upload/");
      	xhr.send(fd);      	
      }
      

      function uploadProgress(evt) {
        try {
          var percentComplete = Math.round(evt.loaded * 100 / evt.total);
          document.getElementById('progress').style.width = percentComplete + "%";
          if (percentComplete == 100) {
              document.getElementById('UploadFileButton').innerHTML = "Writing..";
              document.getElementById('UploadFileButton').disabled = "disabled";
              document.getElementById('UploadFileButton').className = "btn btn-success";
          }
        } catch(e) {
        	throw e;
        }
      }
      function writefile(e){
          e.stopPropagation();
          e.preventDefault();
          document.getElementById('UploadFile').files = e.dataTransfer.files;
          e.target.className = (e.type == "dragover" ? "hover" : "");
      }
      
	    function FileDragHover(e) {
		    e.stopPropagation();
		    e.preventDefault();
		    e.target.className = (e.type == "dragover" ? "hover" : "");
	    }
