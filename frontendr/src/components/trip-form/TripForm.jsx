import React, { useState } from "react";
import "./TripForm.css";

const interestsList = [
    "Beaches",
    "Adventure",
    "Food",
    "Nature",
    "Shopping",
    "Historical Sites",
];

function TripForm({ onGenerate }) {
    const [tripData, setTripData] = useState({
        destination: "",
        startDate: "",
        endDate: "",
        budget: "",
        travelType: "",
        interests: [],
        notes: "",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;

        setTripData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleInterestToggle = (interest) => {
        setTripData((prev) => ({
            ...prev,
            interests: prev.interests.includes(interest)
                ? prev.interests.filter((item) => item !== interest)
                : [...prev.interests, interest],
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (onGenerate) {
            onGenerate(tripData);
        }

        console.log(tripData);
    };

    return (
        <section className="trip-form-section">
            <div className="trip-form-container">
                <h1>AI Travel Itinerary Assistant</h1>
                <p>
                    Enter your trip details and get a personalized day-wise itinerary.
                </p>

                <form onSubmit={handleSubmit} className="trip-form">
                    <div className="form-group">
                        <label>Destination</label>
                        <input
                            type="text"
                            name="destination"
                            placeholder="e.g. Goa, Kerala, Dubai"
                            value={tripData.destination}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="date-grid">
                        <div className="form-group">
                            <label>Start Date</label>
                            <input
                                type="date"
                                name="startDate"
                                value={tripData.startDate}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>End Date</label>
                            <input
                                type="date"
                                name="endDate"
                                value={tripData.endDate}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Budget (₹)</label>
                        <input
                            type="number"
                            name="budget"
                            placeholder="Enter your budget"
                            value={tripData.budget}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Travel Type</label>

                        <div className="radio-group">
                            {["Solo", "Family", "Friends", "Couple"].map((type) => (
                                <label key={type} className="radio-item">
                                    <input
                                        type="radio"
                                        name="travelType"
                                        value={type}
                                        checked={tripData.travelType === type}
                                        onChange={handleChange}
                                    />
                                    {type}
                                </label>
                            ))}
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Interests</label>

                        <div className="interests-container">
                            {interestsList.map((interest) => (
                                <button
                                    type="button"
                                    key={interest}
                                    className={`interest-chip ${tripData.interests.includes(interest)
                                            ? "active"
                                            : ""
                                        }`}
                                    onClick={() => handleInterestToggle(interest)}
                                >
                                    {interest}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Additional Preferences</label>

                        <textarea
                            rows="4"
                            name="notes"
                            placeholder="I prefer local food, less walking, budget hotels...
[6/4/2026 11:06 AM] Cbgk: "
                            value={tripData.notes}
                            onChange={handleChange}
                        />
                    </div>

                    <button type="submit" className="generate-btn">
                        Generate Itinerary
                    </button>
                </form>
            </div>
        </section>
    );
}

export default TripForm;