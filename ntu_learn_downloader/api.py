import re
from typing import List, Tuple, Union, Dict
from urllib.parse import parse_qs, urlencode, urlparse
import json

import bs4
import requests
from bs4 import BeautifulSoup


from ntu_learn_downloader.constants import (
    GET_CONTENT_IDS_URL,
    GET_CONTENT_LIST_URL,
    GET_COURSES_URL,
    LOGINFS_HOSTNAME,
    LOGINFS_URL,
    NTULEARN_AUTH_SAML_URL,
    NTULEARN_URL,
    SAML_SSO_URL,
)
from ntu_learn_downloader.utils import (
    get_content_id_from_listContent_url,
    is_download_link,
    make_GET_request,
)
from ntu_learn_downloader.models import MODEL_TYPES, to_model, Folder
from ntu_learn_downloader.parsing import (
    parse_content_page,
    parse_recorded_lecture_contents,
)


def authenticate(username: str, password: str) -> str:
    """NTU SSO authentication flow to generate BbRouter (NTULearn access token)

    Hit the following endpoints:
    1. GET https://loginfs.ntu.edu.sg/adfs/ls/ to get blank BbRouter
    2. GET https://ntulearn.ntu.edu.sg/auth-saml/saml/login?apId=_140_1&redirectUrl=https%3A%2F%2Fntulearn.ntu.edu.sg%2Fwebapps%2Fportal%2Fexecute%2FdefaultTab'
        to get session cookies
    3. GET https://loginfs.ntu.edu.sg/adfs/ls/?SAMLRequest=<from redirect url> to SAML parameters
    4. GET https://loginfs.ntu.edu.sg/adfs/ls/ to get login form and client-request-id
    5. POST https://loginfs.ntu.edu.sg/adfs/ls/ with SAML params and login credentials to get SAML Response
    6. POST https://ntulearn.ntu.edu.sg/auth-saml/saml/SSO with SAML Response to get authenticated BbRouter

    Arguments:
        username {str} -- username including domain name (e.g. username@student.main.ntu.edu.sg)
        password {str} -- password

    Returns:
        str -- BbRouter token of format: 
        expires:{int},id:{str},signature:{str},site:{str},timeout:{int},user:{str},v:{int},xsrf:{str}
        If there is no user field then authentication has failed
    """
    sess = requests.Session()
    # endpoint 1
    __ntulearn(sess)

    if sess.cookies.get("BbRouter") is None:
        raise Exception("Expected BbRouter in returned cookies")

    # endpoint 2
    saml_response = __ntulearn_auth_saml(sess)
    login_url = saml_response.url
    parsed = urlparse(login_url)
    saml_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    saml_params

    # endpoint 3
    loginfs_response = __loginfs(sess, saml_params)
    soup = BeautifulSoup(loginfs_response.content.decode(), features="lxml")
    form = soup.find_all("form")[0]
    form_url = form.get("action")
    parsed_form_url = urlparse(form_url)
    saml_params = {
        k: v[0] for k, v in parse_qs(parsed_form_url.query).items()
    }  # overwrite saml_params

    # endpoint 4
    auth_response = __post_loginfs(sess, username, password, saml_params, login_url)
    soup = BeautifulSoup(auth_response.content.decode(), features="lxml")
    SAMLResponse = soup.find_all("input")[0].get("value")
    referer = login_url + "&client-request-id=" + saml_params["client-request-id"]

    # endpoint 5
    __ntulearn_SSO(sess, referer, SAMLResponse)

    # check that the BbRouter is authenticated
    BbRouter: str = sess.cookies.get("BbRouter")
    if "user" not in BbRouter:
        raise Exception(
            "Bbrouter: {} does not have user field, it is not authenticated".format(
                BbRouter
            )
        )

    return BbRouter


def get_courses(BbRouter: str) -> List[Tuple[str, str]]:
    """Return list of courses that user is currently reading

    Arguments:
        BbRouter {str} -- authentication token

    Returns:
        List[Tuple[str, str]] -- list of tuples (course name, course_id)
    """
    cookies = {"BbRouter": BbRouter}
    headers = {
        "Connection": "keep-alive",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "X-Prototype-Version": "1.7",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-US,en;q=0.9",
    }

    params = (
        ("cmd", "view"),
        ("serviceLevel", "blackboard.data.course.Course$ServiceLevel:FULL"),
    )
    response = requests.get(
        GET_COURSES_URL,
        headers=headers,
        params=params,  # type: ignore
        cookies=cookies,
    )

    # parse response
    soup = BeautifulSoup(response.content, features="lxml")
    links = soup.find_all("a")

    courses: List[Tuple[str, str]] = []
    for link in links:
        name = link.contents[0]
        if isinstance(name, bs4.element.Tag):
            name = name.text
        # expect fullLink to be of form:
        # link javascript:globalNavMenu.goToUrl('/webapps/blackboard/execute/launcher?type=Course&id=_302242_1&url='); return false;
        fullLink = link.get("onclick")
        matches = re.search(r"type=Course&id=_(\S+)&url=", fullLink)
        if matches is None:
            print("Unable to parse link to get course id: {}".format(fullLink))
            continue
        groups = matches.groups()
        if len(groups) != 1:
            print("Unable to parse link to get course id: {}".format(fullLink))
            continue
        course_id = groups[0]
        courses.append((name, course_id))
    return courses


def get_content_ids(BbRouter: str, course_id: str) -> List[Tuple[str, str]]:
    """returns list of tuples of content name and content ids associated to the course_id

    Arguments:
        BbRouter {str} -- authentication token
        course_id {str} -- course id

    Returns:
        List[Tuple[str, str]] -- list of tuple (content name, content_id)
    """
    params = (
        ("method", "search"),
        ("context", "course_entry"),
        ("course_id", course_id),
    )
    response = make_GET_request(BbRouter, GET_CONTENT_IDS_URL, params)

    soup = BeautifulSoup(response.content.decode(), features="lxml")
    ll = soup.find("ul", {"id": "courseMenuPalette_contents"})
    result: List[Tuple[str, str]] = []
    for c in ll:
        a = c.find("a")
        if a is None:
            continue
        url = a.get("href")
        name = a.text
        content_id = get_content_id_from_listContent_url(url)
        if content_id:
            result.append((name, content_id))
    return result


def get_contents(
    BbRouter: str, course_id: str, content_id: str
) -> List[MODEL_TYPES]:
    # NOTE e.g. "course_id": "_306327_1", "content_id": "_1790226_1"
    soup = make_get_contents_request(BbRouter, course_id, content_id)
    children = [to_model(c) for c in parse_content_page(soup)]
    return children


def make_get_contents_request(
    BbRouter: str, course_id: str, content_id: str
) -> BeautifulSoup:
    params = (("course_id", course_id), ("content_id", content_id))
    response = make_GET_request(BbRouter, GET_CONTENT_LIST_URL, params)
    soup = BeautifulSoup(response.content.decode(), features="lxml")
    return soup


def get_recorded_lecture_contents(BbRouter: str, link: str) -> str:
    """get html of AcuStudio

    Arguments:
        BbRouter {str} -- authentication token
        link {str} -- predownload link to AcuStudio

    Returns:
        str -- html of page
    """
    response = make_GET_request(BbRouter, NTULEARN_URL + link)
    return response.content.decode()


def get_recorded_lecture_download_link(BbRouter: str, predownload_link: str) -> str:
    """get actual mp4 download link from link to Acustudio. This takses a while which is why we 
    defer it until we actially want to download the mp4, hence the need to expose this endpoint

    Arguments:
        BbRouter {str} -- authentication token
        predownload_link {str} -- link to Acustudio

    Returns:
        str -- download link to mp4
    """
    html = get_recorded_lecture_contents(BbRouter, predownload_link)
    return parse_recorded_lecture_contents(html)


def get_file_download_link(BbRouter: str, link: str) -> str:
    """Get the actual download link (contains file name in url)

    Arguments:
        BbRouter {str} -- authentication token
        link {str} -- link

    Returns:
        str -- file download link
    """
    cookies = {"BbRouter": BbRouter}
    headers = requests.head(link, allow_redirects=True, cookies=cookies)
    return headers.url


def get_download_dir(BbRouter: str, course_name: str, course_id: str):
    """Return dict with directory structure of downloadable items (documents and lectures)

    Arguments:
        BbRouter {str} -- authentication token
        course_name {str} -- name of course
        course_id {str} -- course id

    Returns:
        Dict or JSON dump -- Folder dict object, attributes shown below:

        Folder
        - type: "folder"
        - name: string
        - contents: List[Folder, File, RecordedLecture]

        File
        - type: "file"
        - name: string
        - download_link: string

        RecordedLecture
        - type: "recorded_lecture"
        - name: string
        - predownload_link: string
    """

    content_names_ids = get_content_ids(BbRouter, course_id)
    children = [
        Folder(
            name=content_name,
            link=None,
            details="{} folder. Generated by NTULearn Downloader".format(content_name),
            children=get_contents(BbRouter, course_id, content_id),
        )
        for content_name, content_id in content_names_ids
    ]

    folder = Folder(
        name=course_name,
        link=None,
        details="Top level folder for {}. Generated by NTULearn Downloader".format(
            course_name
        ),
        children=children,
    )
    return folder.serialize(BbRouter)


def __ntulearn(session):
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://loginfs.ntu.edu.sg/adfs/ls/",
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = session.get(NTULEARN_URL, headers=headers, allow_redirects=True)
    return response


def __ntulearn_auth_saml(session):
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://ntulearn.ntu.edu.sg/",
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = session.get(
        NTULEARN_AUTH_SAML_URL, headers=headers, allow_redirects=True
    )
    return response


def __loginfs(session, saml_params):

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://ntulearn.ntu.edu.sg/",
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = (
        ("SAMLRequest", saml_params["SAMLRequest"]),
        ("SigAlg", "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"),
        ("Signature", saml_params["Signature"]),
    )

    response = requests.get(LOGINFS_URL, headers=headers, params=params)
    return response


def __post_loginfs(session, username, password, saml_params, login_url):
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "https://loginfs.ntu.edu.sg",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": login_url,
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = (
        ("SAMLRequest", saml_params["SAMLRequest"]),
        ("SigAlg", "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"),
        ("Signature", saml_params["Signature"]),
        ("client-request-id", saml_params["client-request-id"]),
    )

    data = {
        "UserName": username,
        "Password": password,
        "AuthMethod": "FormsAuthentication",
    }

    response = session.post(LOGINFS_URL, headers=headers, params=params, data=data)
    return response


def __ntulearn_SSO(session, referer: str, SAMLResponse: str):
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Origin": LOGINFS_HOSTNAME,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": referer,
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    data = {"SAMLResponse": SAMLResponse}

    response = session.post(SAML_SSO_URL, headers=headers, data=data)
    return response
