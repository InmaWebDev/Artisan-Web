import json
import os


class User:
    def __init__(self, user_id, name, email, edad=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.edad = edad

    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'edad': self.edad
        }

    @staticmethod
    def from_dict(data):
        """Crea un usuario desde un diccionario"""
        return User(
            user_id=data.get('user_id'),
            name=data.get('name'),
            email=data.get('email'),
            edad=data.get('edad')
        )

    def save(self):
        """Guarda el usuario en un archivo JSON"""
        data_dir = os.path.join('src', 'app', 'data', 'user')
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, f'{self.user_id}_user.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @staticmethod
    def load(user_id):
        """Carga un usuario desde un archivo JSON"""
        file_path = os.path.join(
            'src', 'app', 'data', 'user', f'{user_id}_user.json'
        )
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return User.from_dict(data)
        return None

    @staticmethod
    def get_all():
        """Obtiene todos los usuarios guardados"""
        data_dir = os.path.join('src', 'app', 'data', 'user')
        users = []
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('_user.json'):
                    user_id = filename.replace('_user.json', '')
                    user = User.load(user_id)
                    if user:
                        users.append(user)
        return users

    def delete(self):
        """Elimina el archivo del usuario"""
        file_path = os.path.join(
            'src', 'app', 'data', 'user', f'{self.user_id}_user.json'
        )
        if os.path.exists(file_path):
            os.remove(file_path)

    def __repr__(self):
        return f"User(id={self.user_id}, name={self.name}, email={self.email})"
