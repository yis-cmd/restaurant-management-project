"""
restaurant manager 1.1
by yis
"""
import menus
import rest

def main()->None:
    restaurants = rest.Restaurants()
    menu = menus.MainMenu("welcome to the restaurant management app", restaurants)
    menu.run()

if __name__ == "__main__":
    main()