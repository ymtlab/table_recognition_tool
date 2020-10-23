if __name__ == "__main__":
    a = [10, 20, 3, 4]
    print(a)

    print( [ False for i in a if i < 0 ] )
    print( False in [ False for i in a if i < 0 ] )
    
    a = [10, -10, 3, -3]
    print( [ False for i in a if i < 0 ] )
    print( False in [ False for i in a if i < 0 ] )