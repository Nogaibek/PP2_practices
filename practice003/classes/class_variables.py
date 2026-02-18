class folder:
     def __init__ (self, name):
          self.name = name
          self.games = []
          self.videos = []
          self.musics = []
     
     def add_game(self, game):
          self.games.append(game)

     def add_video(self, video):
          self.videos.append(video)

     def add_musics(self, music):
          self.musics.append(music)
     
directory = folder("favorites")

directory.add_game("CS:GO")
directory.add_musics("Adai")
directory.add_video("ICPC final")



