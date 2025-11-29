from flask import Flask, jsonify, request, send_from_directory
import time
import random
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

# --- Mock Data Setup ---
INDIAN_CITIES = {
    'DEL': 'New Delhi', 'BOM': 'Mumbai', 'BLR': 'Bengaluru',
    'MAA': 'Chennai', 'HYD': 'Hyderabad', 'CCU': 'Kolkata',
    'PNQ': 'Pune', 'AMD': 'Ahmedabad'
}

MOCK_BOOKINGS = {}

def generate_flight(flight_number, source_code, dest_code, departure_time, price):
    return {
        'id': f'F{random.randint(1000, 9999)}',
        'flight_number': flight_number,
        'airline': random.choice(['Air India', 'IndiGo', 'SpiceJet', 'Vistara']),
        'source_code': source_code,
        'source_city': INDIAN_CITIES.get(source_code, source_code),
        'dest_code': dest_code,
        'dest_city': INDIAN_CITIES.get(dest_code, dest_code),
        'departure_time': departure_time,
        'duration': f'{random.randint(1, 4)}h {random.randint(0, 59)}m',
        'price': price,
        'stops': random.choice(['Direct', '1 Stop'])
    }

def get_mock_flights(source_code, dest_code, travel_date):
    flights = []
    base_price = random.randint(3000, 15000)
    for i in range(1, 5):
        hour = 6 + i * 3
        flights.append(generate_flight(
            f'{random.choice(["AI", "6E", "UK"])}{random.randint(100, 999)}',
            source_code, dest_code,
            f'{hour:02d}:00',
            base_price + random.randint(-500, 500)
        ))
    return flights

# --- Routes ---

# Serve main page
@app.route('/')
def home():
    return send_from_directory('.', 'RiraXOne.html')

# Serve CSS from root folder
@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

# Serve other HTML pages from static folder
@app.route('/<page>')
def serve_static_html(page):
    if page in ['flight.html', 'book.html', 'boarding.html', 'payment.html']:
        return send_from_directory('static', page)
    return jsonify({'error': 'Page not found'}), 404

# API: search flights
@app.route('/search-flights')
def search_flights():
    source = request.args.get('source', '').upper()
    dest = request.args.get('destination', '').upper()
    date = request.args.get('date')

    if source not in INDIAN_CITIES or dest not in INDIAN_CITIES or source == dest:
        return jsonify({'error': f'Invalid source ({source}) or destination ({dest})'}), 400

    flights = get_mock_flights(source, dest, date)
    return jsonify(flights)

# API: create booking
@app.route('/create-booking', methods=['POST'])
def create_booking():
    data = request.json
    flight_id = data.get('flight_id')
    passengers = data.get('passengers', 1)

    source_code = data.get('source_code', random.choice(list(INDIAN_CITIES.keys())))
    dest_code = data.get('dest_code', random.choice([k for k in INDIAN_CITIES if k != source_code]))

    mock_flight = generate_flight(
        f'M{random.randint(100, 999)}',
        source_code,
        dest_code,
        data.get('departure_time', '10:00'),
        random.randint(5000, 15000)
    )

    total_amount = mock_flight['price'] * passengers
    pnr = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    booking_id = str(int(time.time() * 1000)) + str(random.randint(100, 999))

    booking_details = {
        'booking_id': booking_id,
        'pnr': pnr,
        'flight_id': flight_id,
        'from_code': source_code,
        'from_city': INDIAN_CITIES.get(source_code, source_code),
        'to_code': dest_code,
        'to_city': INDIAN_CITIES.get(dest_code, dest_code),
        'travel_date': data.get('date', '2025-12-25'),
        'departure_time': mock_flight['departure_time'],
        'passengers': passengers,
        'class': data.get('class', 'Economy'),
        'total_amount': total_amount,
        'currency': 'INR',
        'status': 'PENDING_PAYMENT',
        'airline_name': 'RiraXOne Airlines'
    }

    MOCK_BOOKINGS[booking_id] = booking_details
    return jsonify(booking_details), 200

# API: get booking details
@app.route('/booking/<booking_id>')
def get_booking(booking_id):
    booking = MOCK_BOOKINGS.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify(booking)

# API: pay booking
@app.route('/pay-booking', methods=['POST'])
def pay_booking():
    data = request.json
    booking_id = data.get('booking_id')
    booking = MOCK_BOOKINGS.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    booking['status'] = 'CONFIRMED'
    return jsonify({'message': 'Payment successful', 'booking_id': booking_id}), 200

if __name__ == '__main__':
    app.run(debug=True)
