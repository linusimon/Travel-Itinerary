import logo from './logo.svg';
import './App.css';
import TripForm from './components/trip-form/TripForm';
import ItinerarySection from './components/itinerary/ItinerarySection';
import { useRef, useState } from 'react';
import FullScreenLoader from './components/loader/FullScreenLoader';

function App() {


  const sampleItinerary = {
    destination: "Goa",
    budget: 30000,
    days: [
      {
        dayNumber: 1,
        date: "10 Aug 2026",
        activities: [
          {
            time: "09:00 AM",
            title: "Arrival",
            description: "Arrive at Goa Airport and transfer to hotel."
          },
          {
            time: "11:00 AM",
            title: "Calangute Beach",
            description: "Relax and enjoy beach activities."
          },
          {
            time: "01:00 PM",
            title: "Lunch",
            description: "Try local Goan cuisine."
          }
        ]
      },
      {
        dayNumber: 2,
        date: "11 Aug 2026",
        activities: [
          {
            time: "09:00 AM",
            title: "Fort Aguada",
            description: "Explore the historic fort."
          },
          {
            time: "02:00 PM",
            title: "Water Sports",
            description: "Parasailing and jet skiing."
          }
        ]
      }
    ]
  };

  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);

  const itineraryRef = useRef(null);

  const handleGenerate = async (tripData) => {
    setLoading(true);

    itineraryRef.current?.scrollIntoView({
      behaviour: "smooth",
      block: "start"
    })


    //API call here

    setTimeout(() => {
      itineraryRef.current?.scrollIntoView({
        behaviour: "smooth",
        block: "start"
      })
      setItinerary(sampleItinerary);
      setLoading(false);

    }, 2000);
  };
  return (
    <div className="App">
      {/* <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header> */}
      {loading && <FullScreenLoader />}
      <TripForm onGenerate={handleGenerate} />
      <div id='itinerary-section' ref={itineraryRef}>
        <ItinerarySection itinerary={itinerary} loading={loading} />
      </div>
    </div>
  );
}

export default App;
