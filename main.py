
# import csv
# from ultralytics import YOLO
# import cv2
# import pytesseract
# import os

# # Function to create the table if it doesn't exist
# def create_csv():
#     with open('vehicle_data.csv', 'w', newline='') as csvfile:
#         fieldnames = ['vehicle_number', 'bike_image_path']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

# # Function to insert a record into the CSV file
# def insert_record_csv(vehicle_number, bike_image_path):
#     with open('vehicle_data.csv', 'a', newline='') as csvfile:
#         fieldnames = ['vehicle_number', 'bike_image_path']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writerow({'vehicle_number': vehicle_number, 'bike_image_path': bike_image_path})

# # Initialize YOLO models
# person_bike_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/human_on_bike.pt")
# helmet_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/helmet_detector.pt")
# number_plate_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/np_detector_temp.pt")

# # Set up Tesseract OCR
# pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"  # Update with the path to your Tesseract OCR executable

# # Path to the input image file
# image_path = "no_helm7.jpg"  # Update with the path to your image file

# # Read the input image
# frame = cv2.imread(image_path)

# # Detect person on a bike
# person_bike_results = person_bike_model.predict(frame)
# #output_image_path = "output"
# # Process each detection result
# for r in person_bike_results:
#     boxes = r.boxes
#     # Filter detections for person on a bike
#     for box in boxes:
#         cls = box.cls
#         print(person_bike_model.names[int(cls)], person_bike_model.names[int(cls)] == "Person_Bike")
#         if person_bike_model.names[int(cls)] == "Person_Bike":
#             # Crop person on a bike image
#             x1, y1, x2, y2 = box.xyxy[0]
#             person_bike_image = frame[int(y1):int(y2), int(x1):int(x2)]
#             print("bike_co-ordinates")
#             print(x1, y1, x2, y2)
#             # Detect helmet on the person
#             helmet_results = helmet_model.predict(person_bike_image)

#             # Process each helmet detection result
#             for hr in helmet_results:
#                 h_boxes = hr.boxes
#                 # Filter detections for no helmet
#                 for h_bo in h_boxes:
#                     h_cls = h_bo.cls
#                     if not helmet_model.names[int(h_cls)] == "With Helmet" :
#                         # Extract number plate from the person bike image
#                         number_plate_results = number_plate_model.predict(person_bike_image)

#                         # Process each number plate detection result
#                         for npr in number_plate_results:
#                             np_boxes = npr.boxes
#                             # Filter detections for number plate
#                             for np_box in np_boxes:
#                                 np_cls = np_box.cls
#                                 print(number_plate_model.names[int(np_cls)])
#                                 if number_plate_model.names[int(np_cls)] == "license-plate":
#                                     # Crop number plate image
#                                     np_x1, np_y1, np_x2, np_y2 = np_box.xyxy[0]
#                                     print("Crop number plate image")
#                                     print(np_x1, np_y1, np_x2, np_y2)
#                                     number_plate_image = person_bike_image[int(np_y1):int(np_y2),
#                                                          int(np_x1):int(np_x2)]
#                                     # Save the cropped number plate image
#                                     output_file = f"person_violation_2"  # Ensure it's a .jpg file for consistency
#                                     output_path = os.path.join("output", output_file)
#                                     cv2.imwrite("output_images", number_plate_image)

#     #     # Perform OCR on the number plate image
#                                     gray = cv2.cvtColor(number_plate_image, cv2.COLOR_BGR2GRAY)
#                                     text = pytesseract.image_to_string(gray)

#     #     # Insert the data into the CSV file
#                                     insert_record_csv(text, output_path)
#                                     output_image_path = "output_with_bounding_box.jpg"
#                                     cv2.imwrite(output_image_path, frame)
#     #     # Print the extracted text
#                                     print("Number Plate Text:", text)




from ultralytics import YOLO
import cv2
import pytesseract
import os
import sqlite3

# Function to create the table if it doesn't exist
def create_table():
    # Connect to the SQLite database
    conn = sqlite3.connect("vehicle_data.db")
    # Create a cursor object to execute SQL statements
    c = conn.cursor()
    # Create the "vehicles" table with two columns: "vehicle_number" and "bike_image_path"
    # The "IF NOT EXISTS" clause ensures that the table is only created if it doesn't already exist
    c.execute("CREATE TABLE IF NOT EXISTS vehicles (vehicle_number TEXT, bike_image_path TEXT)")
    # Commit the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()

# Function to insert a record into the "vehicles" table
def insert_record(vehicle_number, bike_image_path):
    # Connect to the SQLite database
    conn = sqlite3.connect("vehicle_data.db")
    # Create a cursor object to execute SQL statements
    c = conn.cursor()
    # Insert the record into the "vehicles" table using parameterized SQL statement
    c.execute("INSERT INTO vehicles VALUES (?, ?)", (vehicle_number, bike_image_path))
    # Commit the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()

# Initialize YOLO models
person_bike_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/human_on_bike.pt")
helmet_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/helmet_detector.pt")
number_plate_model = YOLO(r"D:/Final-Year/helmet&np detection major project/models/np_detector_temp.pt")

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"  # Update with the path to your Tesseract OCR executable

output_dir = r"output_images"  # Directory to save the output images
# Set up video capture
video_capture = cv2.VideoCapture(0)  # Use 0 for the default camera or provide the desired camera index

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    # Process frame
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Detect person on a bike
    person_bike_results = person_bike_model.predict(img)

    # Process each detection result
    for r in person_bike_results:
        boxes = r.boxes
        # Filter detections for person on a bike
        for box in boxes:
            cls = box.cls
            print(person_bike_model.names[int(cls)], person_bike_model.names[int(cls)] == "Person_Bike")
            if person_bike_model.names[int(cls)] == "Person_Bike":
                # Crop person on a bike image
                x1, y1, x2, y2 = box.xyxy[0]
                person_bike_image = frame[int(y1):int(y2), int(x1):int(x2)]

                # Detect helmet on the person
                helmet_results = helmet_model.predict(person_bike_image)

                # Process each helmet detection result
                for hr in helmet_results:
                    h_boxes = hr.boxes
                    # Filter detections for no helmet
                    for h_bo in h_boxes:
                        h_cls = h_bo.cls
                        if not helmet_model.names[int(h_cls)] == "With Helmet" :
                            # Extract number plate from the person bike image
                            number_plate_results = number_plate_model.predict(person_bike_image)

                            # Process each number plate detection result
                            for npr in number_plate_results:
                                np_boxes = npr.boxes
                                # Filter detections for number plate
                                for np_box in np_boxes:
                                    np_cls = np_box.cls
                                    print(number_plate_model.names[int(np_cls)])
                                    if number_plate_model.names[int(np_cls)] == "license-plate":
                                        # Crop number plate image
                                        np_x1, np_y1, np_x2, np_y2 = np_box.xyxy[0]
                                        number_plate_image = person_bike_image[int(np_y1):int(np_y2),
                                                             int(np_x1):int(np_x2)]
                                        # Save the cropped number plate image
                                        output_file = f"person_violation_"
                                        output_path = os.path.join("output", output_file)
                                        cv2.imwrite(output_path, person_bike_image)

                                        # Perform OCR on the number plate image
                                        gray = cv2.cvtColor(number_plate_image, cv2.COLOR_BGR2GRAY)
                                        text = pytesseract.image_to_string(gray)
                                        # Example usage
                                        # Create the "vehicles" table if it doesn't exist
                                        create_table()
                                        # Insert two records into the "vehicles" table
                                        insert_record(text, output_path)
                                        # Print the extracted text
                                        print("Number Plate Text:", text)