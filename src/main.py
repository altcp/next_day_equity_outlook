import gc
from functions import get_eda


def cli():

    
    print(" Welcome to Sell Side Quantitative Research (SSQR) ")
    print(" https://github.com/altcp ")

    
    def get_help():
        
        print(" ")
        print(" ")    
        print(" ")
        print(" Usage:  {Command} ")
        print(" ")
        print(" ")
        print(" Available Commands: ")
        print(" ")
        print("   help                    Print this Usage Guide ")
        print("   settings                Configure Hyperparameters ")
        print("   outlook                 Get Next Business Day Equity Outlook ")
        print("   projection              Get Next Period Valuative Projection ")
        print("   exit                    Exit the Application ")
        print(" ")    
        print(" ")
        print(" ")
        
    return None


    get_help()
    ans_one = 0
    
    
    while (ans_one < 1):
        
        input_ans_one = input("SSQR, Enter Command ({help} for Help): ")

        if (input_ans_one == 'settings'):
            print("coming Soon. ")
            print(" ")    
            print(" ")
            
        elif (input_ans_one == 'outlook'):
            get_eda()
            
        elif (input_ans_one == 'projection'):
            get_eda()
    
        elif (input_ans_one == 'help'):
            print("Future Development. ")
            print(" ")    
            print(" ")
        
        elif (input_ans_one == 'exit')
            break
     
        else:
            print("Please enter a valid command. ")
            print(" ")    
            print(" ")
    
    
    #Shut Down 
    print(". ")
    print(". ")    
    print(". ")
    print("  ")
    print("fin")
    print("  ")

    return None


if __name__ == "__main__":
    cli()    
    gc.collect()
    quit()



