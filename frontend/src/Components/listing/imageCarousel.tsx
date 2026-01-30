import { useState } from "react";


export default function GameImageList({ images=[] }: { images: string[] }) {

    const [currentImage,setCurrentImage] = useState(0);

    if (images.length === 0) {
        return (
        <div className="image-carousel">
            <div>
            <h1>NO IMAGES</h1>
            </div>
        </div>
        );
    }

    return (        
        <div className="image-carousel">
            <div className="image-holder">
                <button className="carousel-buttons prev" onClick={() => setCurrentImage(i => Math.max(0, i - 1))}>&lt;</button>
                    <img src={images[currentImage]} alt="Game Image" className="game-image"/>
                <button className="carousel-buttons next" onClick={() => setCurrentImage(i => Math.min(images.length - 1, i + 1))}>&gt;</button>
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
