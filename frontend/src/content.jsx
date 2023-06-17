import React, { useEffect, useState } from 'react';
import pica from 'pica';
import { useNavigate } from 'react-router-dom';
import LogoutBar from './logout';


function Content() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [receivedImage, setReceivedImage] = useState(null);
  const picaInstance = pica();
  const navigate = useNavigate();

  useEffect(() => {
    document.title = 'Inference'
  }, [])

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onloadend = async function () {
      const img = document.createElement('img');
      img.src = reader.result;

      img.onload = async function () {
        const canvas = document.createElement('canvas');
        canvas.width = 360;
        canvas.height = 360;

        await picaInstance.resize(img, canvas);
        const resizedImage = canvas.toDataURL();
        setSelectedImage(resizedImage);
        // console.log(typeof resizedImage);
        await sendImageToServer(resizedImage);
      };
    };
    reader.readAsDataURL(file);
  };

  const sendImageToServer = async (image) => {
    try {
      const response = await fetch('/inference', {
        method: 'POST',
        credentials: "include",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image }),
      });
      if (response.status == 401) {
        navigate('/')
      }
      else if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      else {
        const data = await response.json();
        console.log(data.image);
        setReceivedImage('data:image/png;base64,' + data.image);
      }
    } catch (error) {
      console.error("Error uploading image: ", error);
    }
  };
  
  return (
    <div className="Content">
      <LogoutBar />
      <form>
        <input type="file" accept="image/*" onChange={handleImageUpload} />
      </form>
      <div className="imagesContainer">
        {selectedImage && <img src={selectedImage} alt="Selected" className="leftImage" />}
        {receivedImage && <img src={receivedImage} alt="Received" className="rightImage" />}
      </div>
    </div>
  );
}

export default Content;
