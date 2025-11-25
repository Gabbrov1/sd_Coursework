import { useState } from "react";


export default function GameImageList() {

    const images = [
        "https://picsum.photos/seed/10/300/",
        "https://picsum.photos/seed/1/300",
        "https://picsum.photos/seed/2/300",
        "https://picsum.photos/seed/3/300"
    ];

    const [currentImage,setCurrentImage] = useState(0);
    return (        
        <div className="image-carousel">
            <div className="image-holder">
                <button className="carousel-buttons" onClick={() => setCurrentImage(i => Math.max(0, i - 1))}>&lt;</button>
                    <img src={images[currentImage]} alt="Game Image" className="game-image"/>
                <button className="carousel-buttons" onClick={() => setCurrentImage(i => Math.min(images.length - 1, i + 1))}>&gt;</button>
            </div>
            <div className="image-pagination">
                {images.map((_, idx) => (
                    <a key={idx} 
                    className={`pagination-dot ${currentImage === idx ? "active" : ""}`} 
                    onClick={()=> setCurrentImage(idx) }>o</a>
                ))}
            </div>

        </div>
    );
}
