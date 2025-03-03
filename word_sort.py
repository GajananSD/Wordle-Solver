import random

def word_sorting(gray_list,green_dict,orange_dict,sorted_list):
    if len(sorted_list)==0:
        with open("words.txt", "r") as worddb:
            after_green = []
            for i in worddb:
                word = i[:5]
                flag = 0
                for key in green_dict:
                    pos = green_dict[key]
                    l = len(pos)
                    for j in pos:
                        if word[j]!=key:
                            flag=1
                            break
                    if flag==1:
                        break
                if flag==0:
                    after_green.append(word)
            after_gray = []
            for word in after_green:
                if word[0] in gray_list or word[1] in gray_list or word[2] in gray_list or word[3] in gray_list or word[4] in gray_list:
                    continue
                else:
                    after_gray.append(word)
            after_orange = []
            for word in after_gray:
                flag = 0
                for key in orange_dict:
                    if key not in word:
                        flag = 1
                        break
                    wrong_pos = orange_dict[key]
                    for j in wrong_pos:
                        if word[j]==key:
                            flag=1
                            break    
                if flag==0:
                    after_orange.append(word)
        
    else:
        after_green = []
        for word in sorted_list:
            flag = 0
            for key in green_dict:
                pos = green_dict[key]
                l = len(pos)
                for j in pos:
                    if word[j]!=key:
                        flag=1
                        break
                if flag==1:
                    break
            if flag==0:
                after_green.append(word) 
        after_gray = []
        for word in after_green:
            if word[0] in gray_list or word[1] in gray_list or word[2] in gray_list or word[3] in gray_list or word[4] in gray_list:
                continue
            else:
                after_gray.append(word)
        after_orange = []
        for word in after_gray:
            flag = 0
            for key in orange_dict:
                if key not in word:
                    flag = 1
                    break
                wrong_pos = orange_dict[key]
                for j in wrong_pos:
                    if word[j]==key:
                        flag=1
                        break    
            if flag==0:
                after_orange.append(word)

    if after_orange:
        final_word = random.choice(after_orange)
        return final_word, after_orange
    else: 
        return 'Not available in db',[]
