from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import cv2
import os
import uuid
import logging
from dotenv import load_dotenv
from ai import ( 
    process_img_llm, 
    process_text_math_problem, 
    process_img_llm_SAT, 
    process_text_SAT_problem, 
    process_img_llm_ACT, 
    process_text_ACT_problem, 
    extract_qa_and_store,
    create_index
    ) 

app = Flask(__name__)
CORS(app)
camera = cv2.VideoCapture(0)
capture_folder = 'captured_images'

load_dotenv()
create_index()

if not os.path.exists(capture_folder):
    os.makedirs(capture_folder)


@app.route('/api/math', methods=['POST'])
def math():
    action_type = request.args.get('type')
    if action_type == 'text':
        math_problem = request.json.get('math_problem')
        if math_problem:
            result = process_text_math_problem(math_problem)
            return jsonify({'result': result})
    elif action_type == 'capture':
        success, frame = camera.read()
        if success:
            img_name = os.path.join(capture_folder, "captured_math_image.jpg")
            cv2.imwrite(img_name, frame)
            result = process_img_llm(img_name)
            return jsonify({'result': result['formatted_summary']})
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    return jsonify({'error': 'Invalid action type'}), 400


@app.route('/api/SAT', methods=['POST'])
def sat():
    action_type = request.args.get('type')
    if action_type == 'text':
        sat_problem = request.json.get('sat_problem')
        if sat_problem:
            result = process_text_SAT_problem(sat_problem)
            return jsonify({'result': result})
    elif action_type == 'capture':
        success, frame = camera.read()
        if success:
            img_name = os.path.join(capture_folder, "captured_SAT_image.jpg")
            cv2.imwrite(img_name, frame)
            result = process_img_llm_SAT(img_name)
            return jsonify({'result': result['formatted_summary']})
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    return jsonify({'error': 'Invalid action type'}), 400


@app.route('/api/ACT', methods=['POST'])
def act():
    action_type = request.args.get('type')
    if action_type == 'text':
        act_problem = request.json.get('act_problem')
        if act_problem:
            result = process_text_ACT_problem(act_problem)
            return jsonify({'result': result})
    elif action_type == 'capture':
        success, frame = camera.read()
        if success:
            img_name = os.path.join(capture_folder, "captured_ACT_image.jpg")
            cv2.imwrite(img_name, frame)
            result = process_img_llm_ACT(img_name)
            return jsonify({'result': result['formatted_summary']})
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    return jsonify({'error': 'Invalid action type'}), 400


@app.route('/api/video_feed')
def video_feed():
    def gen_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/qa', methods=['POST'])
def qa_capture():
    # Capture the current frame from the video feed
    success, frame = camera.read()
    if not success:
        logging.error("Failed to capture frame from the camera.")
        return {'error': 'Failed to capture frame'}, 500

    # Save the captured frame as an image
    img_path = os.path.join(capture_folder, f"qa_img.jpg")
    cv2.imwrite(img_path, frame)
    logging.info(f"Image saved to: {img_path}")

    # Process the image and extract Q&A
    result = extract_qa_and_store(img_path)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
