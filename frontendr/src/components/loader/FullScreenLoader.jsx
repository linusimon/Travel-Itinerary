import "./FullScreenLoader.css";

function FullScreenLoader() {
    return (
        <div className="loader-overlay">
            <div className="loader-content">
                <div className="loader-spinner"></div>

                <h2>Generating Your Itinerary</h2>

                <p>
                    Finding attractions, routes, timings and
                    personalized recommendations...
                </p>
            </div>
        </div>
    );
}

export default FullScreenLoader;