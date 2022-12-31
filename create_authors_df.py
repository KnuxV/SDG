"""
Created by kevin-desktop, on the 30/12/2022
From a WOS database annotated with SDG and DT (row=publications), we convert to an author DB (row = email)
"""
import copy
import itertools
import typing

import numpy as np
import pandas as pd
import re
import math
from collections import Counter
import tqdm
import re
import itertools
import copy


def match_email_name(emails: typing.List, names: typing.List) -> dict:
    """
    This function create pairs of email:mail from the two input lists if words or part of words in the name can be found
    in the email.
    Args:
        emails: a list of emails
        names:  a list of names

    Returns:
        a dictionary {email:name for each pair that can be linked to the input}

    """
    # res dictionary
    dic_mails_names = dict()

    # If one of the two input lists are NAN (type==float), we return an empty dic
    if type(emails) == float or type(names) == float:
        return dic_mails_names

    # They need to be set, to avoid repetition
    # Sorting
    names.sort(key=len, reverse=True)
    names = set(names)
    emails = {e.lower() for e in set(emails)}

    def check_names_in_email(e: str, mode="full_word"):
        """
        Intermediate function, embedded. For each email, we have 3 ways of looking for a match (3 modes)
        combi: first_name and last_name in email or firstname[0] + last_name or lastname[0]+ firstname
        full_word : the full_name is split into words, and one of these words must be in the email
        chunk : At least the first 3 characters of a word must be in the email
        ini: first letter of each word must be in the email (Kevin Michoud ==> km or mk)
        Args:
            e:
            mode: str 'full_word', 'chunk', 'ini', combi

        Returns: None

        """
        for fn in copy.deepcopy(names):
            rootless_email = e.split("@")[0]
            sn = [s for s in re.split(r'\W+', fn) if len(s) > 0]

            if mode == "combi" and len(sn) == 2:
                # check if combo of firstname + lastname in rootless email
                if (sn[0].lower() in rootless_email and sn[1][0].lower() in rootless_email) or \
                        (sn[0][0].lower() in rootless_email and sn[1].lower() in rootless_email):
                    dic_mails_names[e] = fn
                    emails.remove(e)
                    names.remove(fn)
                    return None
            for w in [w for w in sn if len(w) > 2]:
                # First
                if mode == "full_word":
                    if w.lower() in rootless_email:
                        # If the word in the name of the author
                        # is present in the email and at least 3 characters, we consider that they are linked

                        # update dict, remove from both sets, and skip the other words
                        # in the name
                        dic_mails_names[e] = fn
                        emails.remove(e)
                        names.remove(fn)
                        return None
                elif mode == "chunk":
                    if w[0:2].lower() in rootless_email:
                        # If at least 3 characters of a word in the name of the author
                        # is present in the email, we consider that they are linked

                        # update dict, remove from both sets, and skip the other words
                        # in the name
                        dic_mails_names[e] = fn
                        emails.remove(e)
                        names.remove(fn)
                        return None
            if mode == "ini":
                # Looking for a variation of first letter of firstnames and lastnames
                initials = [w[0].lower() for w in sn if len(w) > 0]
                for combo in set(itertools.permutations(initials)):
                    if "".join(combo) in rootless_email:
                        dic_mails_names[e] = fn
                        emails.remove(e)
                        names.remove(fn)
                        return None
                # Case sn = ['Ye', 'Ben', 'Haobin'] ==> em = 'yehb3@mail.sysu.edu.cn'
                # Check if one of the word has len == 2, and consider initial as two letters
                doit = False
                for w in sn:
                    if len(w) == 2:
                        doit = True
                if doit:
                    initials = []
                    for w in sn:
                        if 0 < len(w) < 3:
                            initials.append(w.lower())
                        elif len(w) > 2:
                            initials.append(w[0].lower())
                    for combo in set(itertools.permutations(initials)):
                        if "".join(combo) in rootless_email:
                            dic_mails_names[e] = fn
                            emails.remove(e)
                            names.remove(fn)
                            return None

    # We go through once first, looking for combinations of lastnames and firstnames when ONLY two words in a name
    for email in copy.deepcopy(emails):
        check_names_in_email(e=email, mode="combi")
    # We go through once first, looking for full_word of more than 2 letters
    for email in copy.deepcopy(emails):
        check_names_in_email(e=email, mode="full_word")
    # Then, for chunk of words of at least 3 characters
    for email in copy.deepcopy(emails):
        check_names_in_email(e=email, mode="chunk")

    # Lastly, we check for initials
    for email in copy.deepcopy(emails):
        check_names_in_email(e=email, mode="ini")

    # Once, we've done the search, if there's only one email and one name left in the sets,
    # We match them
    if len(names) == len(emails) == 1:
        dic_mails_names[emails.pop()] = names.pop()

    # Tag emails left as "no_match"
    if len(emails) > 0:
        for email in emails:
            dic_mails_names[email] = "no_match"
    return dic_mails_names


def create_authors_df(dataframe, return_type="dataframe") -> pd.DataFrame | dict:
    """
    From a database of publications, create and return a dataframe (or dictionary) with rows (or keys) equal to each
    email address present in the EM column of the original df.
    Columns (or values) returned are :
    - names = a set of names linked to the email
    - total_publications (int) = number of publications by that email
    - lst_publications (list) = a list of UT published by that email
    - years (list) = a list pf years, for the publication year of every publication of that email.
    - total_citations (int) = the sum of citations of every publication of that email.
    - SDG (Counter) = Counter of every SDG annotated in publications of that email.
    - DT (Counter) =  Counter of every DT annotated in publications of that email.
    - keywords (Counter) = Counter of every keyword (WC colum) in publications of that email.
    Args:
        return_type: "dataframe" or "dic"
        dataframe: a dataframe of publications

    Returns:
        pd.Dataframe or dict()
    """
    idx = {name: ind for ind, name in enumerate(dataframe.columns)}
    dic_authors = dict()

    def ini_dic_authors(e):
        """
        Simple function which initialize the dic_authors dictionary for the given email e
        Args:
            e: an email

        Returns:
            Nothing
        """
        dic_authors[e] = {"name": set(), "total_publications": 0, "lst_publications": set(), "years": [],
                          "total_citations": 0,
                          "SDG": Counter(), "DT": Counter(), "keywords": Counter()}

    for row in tqdm.tqdm(dataframe.itertuples(index=False, name=None), total=dataframe.shape[0]):

        # For each publication, we run the function match_match_email_name to get a dic of matching pair {email:name}
        af = row[idx['AF']]
        em = row[idx['EM']]
        if type(af) != float:
            lst_names = af.split("; ")
        else:
            continue
        if type(em) != float:
            lst_emails = em.split("; ")
        else:
            continue
        dic_emails = match_email_name(emails=lst_emails, names=lst_names)

        # For each pair email:name, we init the dictionary with the mail if necessary, and we update with info in the
        # row of the dataframe.
        for email, name in dic_emails.items():
            if email not in dic_authors:
                ini_dic_authors(email)
            # name
            dic_authors[email]['name'].add(name)
            # Nb publications
            dic_authors[email]['total_publications'] += 1
            # List of publications ==> UT
            ut = row[idx['UT']]
            dic_authors[email]['lst_publications'].add(ut)
            # Years
            py = row[idx['PY']]
            dic_authors[email]["years"].append(py)
            # total citations
            dic_authors[email]['total_citations'] += int(row[idx['TC']])
            # SDG
            set_sdg = row[idx['lst_SDG']]
            dic_authors[email]['SDG'].update(set_sdg)
            # DT
            set_dt = row[idx['lst_DT']]
            dic_authors[email]['DT'].update(set_dt)
            # WC <=> keywords
            keywords = row[idx['WC']]
            if type(keywords) == str:
                keywords = keywords.split("; ")
                dic_authors[email]['keywords'].update(keywords)

    if return_type in ["dataframe", "database", "df"]:
        df_authors = pd.DataFrame.from_dict(dic_authors, orient='index')
        return df_authors
    elif return_type in ['dic', 'dictionary']:
        return dic_authors
    else:
        print(f'The return type you choose is incorrect\nYou\'ve chosen {return_type}.')


if __name__ == '__main__':
    # # Load Dataframe
    # df_inter_path = "data/dataframes/inter.pkl"
    # df_inter = pd.read_pickle(df_inter_path)
    #
    # inter_authors = create_authors_df(df_inter)
    # inter_authors.to_pickle("data/dataframes/inter_authors.pkl")

    # Load Dataframe
    df_all_path = "data/dataframes/all_nodups_shorten.pkl"
    df_all = pd.read_pickle(df_all_path)

    df_all_authors = create_authors_df(df_all)
    df_all_authors.to_pickle("data/dataframes/all_nodups_authors.pkl")

