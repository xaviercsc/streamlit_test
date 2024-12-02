import streamlit as st
import pandas as pd
import json
from datetime import date

# Function to load requests from a JSON file
def load_requests(file_path):
    try:
        with open(file_path, 'r') as file:
            return pd.DataFrame(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame(columns=[
            'Request Number', 'Open Date', 'Close Date', 'Request Status', 
            'Sub Task', 'Assigned To', 'Status Notes'
        ])

# Function to save requests to a JSON file
def save_requests(dataframe, file_path):
    dataframe['Open Date'] = dataframe['Open Date'].astype(str)
    dataframe['Close Date'] = dataframe['Close Date'].astype(str)
    with open(file_path, 'w') as file:
        json.dump(dataframe.to_dict(orient='records'), file, indent=4)

# Initialize or load requests data
file_path = 'request_tracker.json'
if 'requests' not in st.session_state:
    st.session_state['requests'] = load_requests(file_path)

def main():
    st.title("Request Tracker")

    # Search and filter options
    st.sidebar.header("Search and Filter")
    search_number = st.sidebar.text_input("Search by Request Number")
    search_subtask = st.sidebar.text_input("Search by Sub Task")
    search_user = st.sidebar.text_input("Search by Assigned To")
    date_range = st.sidebar.date_input("Filter by Date Range", [])
    
    filtered_data = st.session_state['requests']

    # Apply filtering
    if search_number:
        filtered_data = filtered_data[filtered_data['Request Number'].str.contains(search_number, case=False, na=False)]
    if search_subtask:
        filtered_data = filtered_data[filtered_data['Sub Task'].str.contains(search_subtask, case=False, na=False)]
    if search_user:
        filtered_data = filtered_data[filtered_data['Assigned To'].str.contains(search_user, case=False, na=False)]
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filtered_data[
            (pd.to_datetime(filtered_data['Open Date']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(filtered_data['Close Date']) <= pd.to_datetime(end_date))
        ]

    # Display the filtered requests
    st.subheader("Filtered Requests")
    st.dataframe(filtered_data)

    # Form for entering request information
    with st.form("request_form"):
        request_number = st.text_input("Request Number")
        open_date = st.date_input("Open Date", date.today())
        close_date = st.date_input("Close Date", date.today())
        request_status = st.selectbox("Request Status", ["Open", "In Progress", "Closed"])
        sub_task = st.text_input("Sub Task")
        assigned_to = st.text_input("Assigned To")
        status_notes = st.text_area("Status Notes")

        # Submit button
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_request = pd.DataFrame([{
                'Request Number': request_number,
                'Open Date': open_date.strftime('%Y-%m-%d'),
                'Close Date': close_date.strftime('%Y-%m-%d'),
                'Request Status': request_status,
                'Sub Task': sub_task,
                'Assigned To': assigned_to,
                'Status Notes': status_notes
            }])

            st.session_state['requests'] = pd.concat([st.session_state['requests'], new_request], ignore_index=True)
            save_requests(st.session_state['requests'], file_path)
            st.success("Request added successfully!")

    # Update and delete options
    st.subheader("Update or Delete Entries")
    if not filtered_data.empty:
        selected_index = st.selectbox("Select Request to Update/Delete", filtered_data.index)

        if st.button("Update"):
            with st.form("update_form"):
                # Capture updated values
                updated_request_number = st.text_input("Update Request Number", value=filtered_data.loc[selected_index, 'Request Number'])
                updated_open_date = st.date_input("Update Open Date", value=pd.to_datetime(filtered_data.loc[selected_index, 'Open Date']))
                updated_close_date = st.date_input("Update Close Date", value=pd.to_datetime(filtered_data.loc[selected_index, 'Close Date']))
                updated_request_status = st.selectbox("Update Request Status", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(filtered_data.loc[selected_index, 'Request Status']))
                updated_sub_task = st.text_input("Update Sub Task", value=filtered_data.loc[selected_index, 'Sub Task'])
                updated_assigned_to = st.text_input("Update Assigned To", value=filtered_data.loc[selected_index, 'Assigned To'])
                updated_status_notes = st.text_area("Update Status Notes", value=filtered_data.loc[selected_index, 'Status Notes'])

                # Button to save changes
                if st.form_submit_button("Save Changes"):
                    # Update the main DataFrame with the new values
                    st.session_state['requests'].loc[selected_index, 'Request Number'] = updated_request_number
                    st.session_state['requests'].loc[selected_index, 'Open Date'] = updated_open_date.strftime('%Y-%m-%d')
                    st.session_state['requests'].loc[selected_index, 'Close Date'] = updated_close_date.strftime('%Y-%m-%d')
                    st.session_state['requests'].loc[selected_index, 'Request Status'] = updated_request_status
                    st.session_state['requests'].loc[selected_index, 'Sub Task'] = updated_sub_task
                    st.session_state['requests'].loc[selected_index, 'Assigned To'] = updated_assigned_to
                    st.session_state['requests'].loc[selected_index, 'Status Notes'] = updated_status_notes

                    # Save the updated DataFrame to the JSON file
                    save_requests(st.session_state['requests'], file_path)
                    st.success("Request updated successfully!")
                    st.experimental_rerun()  # Refresh the app to reflect changes

        if st.button("Delete"):
            st.session_state['requests'] = st.session_state['requests'].drop(selected_index).reset_index(drop=True)
            save_requests(st.session_state['requests'], file_path)
            st.success("Request deleted successfully!")
            st.experimental_rerun()  # Refresh the app to reflect changes

if __name__ == "__main__":
    main()
