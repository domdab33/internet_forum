import streamlit as st
import pyodbc
import matplotlib.pyplot as plt



if 'actual_user_id' not in st.session_state:
    st.session_state.actual_user_id = 0
    
if 'actual_user_id' not in st.session_state:
    st.session_state.actual_post_id = 0
    
if 'actual_page' not in st.session_state:
    st.session_state.actual_page = 'auth'



def authenticate(user_name, password):
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
    cursor = cnxn.cursor()

    query = f"SELECT COUNT(*) FROM Users WHERE username = ? AND password = ?;" 
    cursor.execute(query, (user_name, password))

    result = cursor.fetchone()
    count = result[0]
    
    if count == 1:
        query = f"SELECT id FROM Users WHERE username = ? AND password = ?;"
        cursor.execute(query, (user_name, password))
        result = cursor.fetchone()
        
        st.session_state.actual_user_id = result[0]
        success =  True
    else:
        success = False

    cnxn.close()
    return success


def register(user_name, password):  
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    query = f"SELECT COUNT(*) FROM Users WHERE username =  ?;"
    cursor.execute(query, (user_name))
    result = cursor.fetchone()
    count = result[0]
    
    if count == 0 and not user_name == "" and not password == "" :
        query = f"INSERT INTO users (username, password) VALUES (?, ?);"
        cursor = cnxn.cursor()
        cursor.execute(query, (user_name, password))
        cnxn.commit()
        success =  1
    else:
        success =  0
    cnxn.close()
    return success


def change_page(new_page):
    st.session_state.actual_page = new_page
    st.experimental_rerun()
    
    
def user_home_page():
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    query = f"SELECT username FROM Users WHERE id = {st.session_state.actual_user_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    actual_user_name = result[0]
    
    st.title("Jestes zalogowany jako: " + actual_user_name)
    
    if st.button("Wyloguj się"):
        change_page('auth')
    
    if st.button("Dodaj post"):
        change_page('new_post')
        
    if st.button("statystyki"):
        change_page('stats')
        
    query = f"SELECT content, username, Posts.id FROM Posts JOIN Users ON Users.id = Posts.user_id;"
    cursor.execute(query)
    result = cursor.fetchall()
    
    st.title("Dodane posty")
    for post in reversed(result):
        if st.button(post[0],post[2]):
            st.session_state.actual_post_id = post[2]
            change_page('post_detail')
        st.write("dodane przez: "+ post[1])
            
        
    cnxn.close()
    

    
def auth_page():
    st.title("Zaloguj się lub zarejestruj")
    
    
    user_name = st.text_input("Nazwa użytkownika")
    password = st.text_input("Hasło", type="password")
    
    
    if st.button("Zaloguj"):
        if not authenticate(user_name, password):
            st.error("Nieprawidłowa nazwa użytkownika lub hasło")
        else:
            change_page('user_home')
    

    if st.button("Zarejestruj"):
        if register(user_name, password):
            st.success("Rejestracja przebiegła pomyslnie")
        else:
            st.error("Błąd rejestracji")

        
def new_post_page():
    post_content = st.text_input("Co chcesz napisać?")
    if st.button("Opublikuj"): 
        cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        query = f"INSERT INTO Posts (content,user_id) VALUES (?, ?);"
        cursor.execute(query, (post_content, st.session_state.actual_user_id))
        cnxn.commit()
        change_page('user_home')
        cnxn.close()
        
        
def post_detail_page():
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    query = f"SELECT username FROM Users WHERE id = {st.session_state.actual_user_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    actual_user_name = result[0]
    st.title("Jestes zalogowany jako: " + actual_user_name)
    
    if st.button("Wyloguj się"):
        change_page('auth')
        
    if st.button("Dodaj komentarz"):
        change_page('new_comment')
        
    if st.button("Wróć do strony głównej"):
        change_page('user_home')
        
    query = f"SELECT Posts.content FROM Posts WHERE id = {st.session_state.actual_post_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    st.title(result[0])
    query = f"SELECT Comments.content, username, Posts.content FROM Posts JOIN Comments ON Comments.post_id = Posts.id JOIN Users ON Users.id = Comments.user_id WHERE post_id = {st.session_state.actual_post_id};"
    cursor.execute(query)
    result = cursor.fetchall()
    try:
        first_comment = result[0]
        st.title("Komentarze: ")
        for comment in result:
            st.subheader(comment[0])
            st.write("Dodane przez: " + comment[1])
    except:
        st.write("Ten post nie ma jeszcze komentarzy")
    
    

def new_comment_page():
    comment_content = st.text_input("Co chcesz napisać?")
    if st.button("Opublikuj"): 
        cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        query = f"INSERT INTO Comments (content,user_id,post_id) VALUES (?, ?,?);"
        cursor.execute(query, (comment_content, st.session_state.actual_user_id, st.session_state.actual_post_id))
        cnxn.commit()
        change_page('post_detail')
        cnxn.close()
    
def stats_page():
        
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS22;Database=internet_forum;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    query = f"SELECT COUNT(Posts.id), Users.username FROM Users LEFT OUTER JOIN Posts ON Posts.user_id = Users.id GROUP BY Users.username;"
    cursor.execute(query)
    post_count = []
    usernames = []
    result = cursor.fetchall()

    
    for i in range(len(result)):
        post_count.extend([result[i][0]])
        usernames.extend([result[i][1]])
    
    
    fig, ax = plt.subplots()
    ax.bar(usernames, post_count)
    
    st.title("Ilosć postów napisanych przez poszczególnych użytkowników")
    
    st.pyplot(fig)
    cnxn.close()
    
    if st.button("Wróć do strony głównej"):
        change_page('user_home')
    

if st.session_state.actual_page == 'auth':
    auth_page()
elif st.session_state.actual_page =='user_home':
    user_home_page()
elif st.session_state.actual_page =='new_post':
    new_post_page()
elif st.session_state.actual_page =='post_detail':
    post_detail_page()
elif st.session_state.actual_page =='new_comment':
    new_comment_page()
elif st.session_state.actual_page =='stats':
    stats_page()
    




    
    
    
        



