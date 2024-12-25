import pygame
import mysql.connector
from tkinter import Tk, Label, Button, Listbox, filedialog, Entry, Toplevel, messagebox

def initialize_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            artist VARCHAR(255) NOT NULL,
            genre VARCHAR(255),
            filepath VARCHAR(255) NOT NULL
        )
    ''')

    # Create a table for user logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute("SHOW TRIGGERS LIKE 'before_insert_song'")
    trigger_exists = cursor.fetchone()

    if not trigger_exists:
        # Drop the trigger if it exists
        cursor.execute("DROP TRIGGER IF EXISTS before_insert_song")


    # Trigger to automatically update the genre of a song to "Unknown" when a new song is added without specifying a genre
    cursor.execute('''
        CREATE  TRIGGER before_insert_song
        BEFORE INSERT ON songs
        FOR EACH ROW
        BEGIN
            IF NEW.genre IS NULL OR NEW.genre = '' THEN
                SET NEW.genre = 'Unknown';
            END IF;
        END
    ''')
    cursor.execute("SHOW TRIGGERS LIKE 'after_insert_user_login'")
    trigger_exists = cursor.fetchone()

    if not trigger_exists:
        # Drop the trigger if it exists
        cursor.execute("DROP TRIGGER IF EXISTS after_insert_user_login")


    # Trigger to log user logins
    cursor.execute('''
        CREATE TRIGGER after_insert_user_login
        AFTER INSERT ON users
        FOR EACH ROW
        BEGIN
            INSERT INTO user_log (user_id) VALUES (NEW.id);
        END
    ''')


    
    connection.commit()
    connection.close()

# Function to add a user to the database
def add_user(username, password, role):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s)
    ''', (username, password, role))

    connection.commit()
    connection.close()

# Function to check if the given username and password are correct
def check_login_credentials(username, password):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE username = %s AND password = %s
    ''', (username, password))

    user = cursor.fetchone()

    connection.close()

    return user

# Function to create a simple music player with Tkinter GUI
def music_player_with_gui(username, role):
    pygame.init()
    pygame.mixer.init()

    current_song_index = 0
    songs = []

    def play_song():
        nonlocal current_song_index, songs
        if songs:
            pygame.mixer.music.load(songs[current_song_index][4])
            pygame.mixer.music.play()
            status_label.config(text=f"Now playing: {songs[current_song_index][1]} - {songs[current_song_index][2]}", fg="green")

    def stop_song():
        pygame.mixer.music.stop()
        status_label.config(text="Music stopped.", fg="red")

    def pause_song():
        pygame.mixer.music.pause()
        status_label.config(text="Music paused.", fg="orange")

    def resume_song():
        pygame.mixer.music.unpause()
        status_label.config(text=f"Resumed: {songs[current_song_index][1]} - {songs[current_song_index][2]}", fg="green")

    def next_song():
        nonlocal current_song_index, songs
        current_song_index = (current_song_index + 1) % len(songs)
        play_song()

    def previous_song():
        nonlocal current_song_index, songs
        current_song_index = (current_song_index - 1) % len(songs)
        play_song()

    def open_file_dialog():
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav")])
        entry_file_path.delete(0, "end")
        entry_file_path.insert(0, file_path)

    def add_song_gui():
        title = entry_title.get()
        artist = entry_artist.get()
        genre = entry_genre.get()
        filepath = entry_file_path.get()

        add_song(title, artist, genre, filepath)
        update_song_list()
        status_label.config(text="Song added successfully!", fg="blue")

    def delete_selected_song():
        selected_index = songs_listbox.curselection()
        if selected_index:
            song_id_to_delete = songs[selected_index[0]][0]
            delete_song(song_id_to_delete)
            update_song_list()
            status_label.config(text="Song deleted successfully!", fg="purple")

    def update_song_list():
        songs_listbox.delete(0, "end")
        songs.clear()
        songs.extend(get_all_songs())
        for song in songs:
            songs_listbox.insert("end", f"{song[1]} - {song[2]}")

    def play_selected_song(event):
        nonlocal current_song_index
        selected_index = songs_listbox.curselection()
        if selected_index:
            current_song_index = selected_index[0]
            play_song()

    def show_admin_features():
        admin_window = Toplevel(root)
        admin_window.title("Admin Features")
        admin_window.geometry("300x150")
        admin_window.configure(bg="BLACK")

        btn_view_users = Button(admin_window, text="View Users", command=view_users, bg="seashell", fg="black")
        btn_view_users.pack(pady=10)

    def view_users():
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Nandhu18786!",
            database="musicplayer1"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        connection.close()

        user_list = "\n".join([f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}" for user in users])
        messagebox.showinfo("User List", user_list)

    root = Tk()
    root.title(f"Music Player - {username}")
    root.configure(bg="BLACK")  # Background color

    label_title = Label(root, text="Title:", bg="RED")  # Background color
    label_artist = Label(root, text="Artist:", bg="LIGHT BLUE")  # Background color
    label_genre = Label(root, text="Genre:", bg="LIGHT GREEN")  # Background color
    label_file_path = Label(root, text="File Path:", bg="GOLD")  # Background color
    entry_title = Entry(root)
    entry_artist = Entry(root)
    entry_genre = Entry(root)
    entry_file_path = Entry(root)
    btn_open_file_dialog = Button(root, text="Open File Dialog", command=open_file_dialog, bg="lightcoral", fg="black")  # Background and text color
    btn_add_song = Button(root, text="Add Song", command=add_song_gui, bg="paleturquoise", fg="black")  # Background and text color
    btn_play = Button(root, text="Play", command=play_song, bg="chocolate", fg="white")  # Background and text color
    btn_stop = Button(root, text="Stop", command=stop_song, bg="seashell", fg="black")  # Background and text color
    btn_pause = Button(root, text="Pause", command=pause_song, bg="chocolate", fg="white")  # Background and text color
    btn_resume = Button(root, text="Resume", command=resume_song, bg="seashell", fg="black")  # Background and text color
    btn_next = Button(root, text="Next", command=next_song, bg="seashell", fg="black")  # Background and text color
    btn_previous = Button(root, text="Previous", command=previous_song, bg="chocolate", fg="white")  # Background and text color
    btn_delete = Button(root, text="Delete", command=delete_selected_song, bg="seashell", fg="black")  # Background and text color
    status_label = Label(root, text="", bg="BLACK")
    

    label_title.grid(row=0, column=0, sticky="e")
    label_artist.grid(row=1, column=0, sticky="e")
    label_genre.grid(row=2, column=0, sticky="e")
    label_file_path.grid(row=3, column=0, sticky="e")
    entry_title.grid(row=0, column=1, columnspan=2)
    entry_artist.grid(row=1, column=1, columnspan=2)
    entry_genre.grid(row=2, column=1, columnspan=2)
    entry_file_path.grid(row=3, column=1, columnspan=2)
    btn_open_file_dialog.grid(row=3, column=3)
    btn_add_song.grid(row=4, column=0, columnspan=4)
    btn_play.grid(row=5, column=0)
    btn_stop.grid(row=5, column=1)
    btn_pause.grid(row=5, column=2)
    btn_resume.grid(row=5, column=3)
    btn_next.grid(row=6, column=0)
    btn_previous.grid(row=6, column=1)
    btn_delete.grid(row=6, column=2)
    status_label.grid(row=7, column=0, columnspan=4)

    songs_listbox = Listbox(root, selectmode="SINGLE", width=50, height=10, bg="BLACK", fg="WHITE")  # Background color
    songs_listbox.grid(row=8, column=0, columnspan=4, pady=10)
    songs_listbox.bind("<Double-Button-1>", play_selected_song)

    update_song_list()

    if role == "admin":
        show_admin_features()

    root.mainloop()
def delete_song(song_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    cursor.execute('''
        DELETE FROM songs
        WHERE id = %s
    ''', (song_id,))

    connection.commit()
    connection.close()
def add_song(title, artist, genre, filepath):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO songs (title, artist, genre, filepath)
        VALUES (%s, %s, %s, %s)
    ''', (title, artist, genre, filepath))

    connection.commit()
    connection.close()
def get_all_songs():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandhu18786!",
        database="musicplayer1"
    )
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()

    connection.close()
    return songs

def show_login_window():
    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x250")
    login_window.configure(bg="BLACK") 

    Label(login_window, text="Username:", bg="chocolate", fg="white").pack(pady=10)
    entry_username = Entry(login_window)
    entry_username.pack(pady=5)

    Label(login_window, text="Password:", bg="chocolate", fg="white").pack(pady=10)
    entry_password = Entry(login_window, show="*")
    entry_password.pack(pady=5)

    Button(login_window, text="Login", command=lambda: on_login(login_window, entry_username.get(), entry_password.get())).pack(pady=10)
    Button(login_window, text="Add User", command=lambda: add_user_gui(login_window)).pack(pady=10)

def add_user_gui(parent_window):
    add_user_window = Toplevel(parent_window)
    add_user_window.title("Add User")
    add_user_window.geometry("300x250")
    add_user_window.configure(bg="BLACK") 

    Label(add_user_window, text="New Username:", bg="chocolate", fg="white").pack(pady=10)
    entry_new_username = Entry(add_user_window)
    entry_new_username.pack(pady=5)

    Label(add_user_window, text="New Password:", bg="chocolate", fg="white").pack(pady=10)
    entry_new_password = Entry(add_user_window, show="*")
    entry_new_password.pack(pady=5)

    Label(add_user_window, text="Role (admin/user):", bg="chocolate", fg="white").pack(pady=10)
    entry_role = Entry(add_user_window)
    entry_role.pack(pady=5)

    Button(add_user_window, text="Add User", command=lambda: on_add_user(add_user_window, entry_new_username.get(), entry_new_password.get(), entry_role.get())).pack(pady=10)

def on_add_user(add_user_window, new_username, new_password, role):
    add_user(new_username, new_password, role)
    messagebox.showinfo("User Added", f"User {new_username} added successfully!")
    add_user_window.destroy()

def on_login(login_window, username, password):
    user = check_login_credentials(username, password)
    if user:
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        login_window.destroy()
        root.deiconify()  # Show the main window
        music_player_with_gui(username, user[3])  # Pass role to the music player
    else:
        messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")


    # You can add more widgets and customize the content of your custom window here

if __name__ == "__main__":
    root = Tk()
    root.title("Main Window")  # Give the main window a title
    root.withdraw()  # Hide the main window initially

    initialize_database()
    show_login_window()

    root.mainloop()