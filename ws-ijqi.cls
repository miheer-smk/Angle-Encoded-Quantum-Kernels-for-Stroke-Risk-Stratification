%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% ws-ijqi.cls -- LOCAL STAND-IN for the official World Scientific class file
%% for the International Journal of Quantum Information.
%%
%% The official ws-ijqi.cls is distributed by World Scientific from the journal
%% submission-guidelines page and is not redistributable, so it is not included
%% in this repository. This file reproduces the *macro interface* of the
%% official class (\markboth, \title, \author, \address, \maketitle, the
%% history environment, abstract, \keywords, \ccode, superscript numeric
%% citations, 5in text block) so that ijqi_stroke_qksp.tex compiles unmodified.
%%
%% TO PRODUCE THE CAMERA-READY FILE: download the official ws-ijqi.cls from
%%   https://www.worldscientific.com/page/ijqi/submission-guidelines
%% and drop it in this directory, replacing this file. The manuscript source
%% needs no changes.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ws-ijqi}[2026/07/31 v1.0 IJQI stand-in class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[10pt,a4paper,twoside]{article}

\RequirePackage{mathptmx}
\RequirePackage[T1]{fontenc}
\RequirePackage{graphicx}
\RequirePackage{amsmath,amssymb}
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{url}

%% ---------------------------------------------------------------- page layout
\setlength{\textwidth}{5in}
\setlength{\textheight}{8.6in}
\setlength{\oddsidemargin}{\paperwidth}
\addtolength{\oddsidemargin}{-\textwidth}
\setlength{\oddsidemargin}{0.5\oddsidemargin}
\addtolength{\oddsidemargin}{-1in}
\setlength{\evensidemargin}{\oddsidemargin}
\setlength{\topmargin}{-0.35in}
\setlength{\headheight}{24pt}
\setlength{\headsep}{12pt}
\setlength{\footskip}{0pt}
\setlength{\parindent}{16pt}
\setlength{\arraycolsep}{2pt}
\setlength{\emergencystretch}{2em}
\raggedbottom

%% ------------------------------------------------------------- running heads
\def\ws@leftmark{Authors' Names}
\def\ws@rightmark{Instructions for Typing Manuscripts (Paper's Title)}
\renewcommand{\markboth}[2]{\gdef\ws@leftmark{#1}\gdef\ws@rightmark{#2}}
%% The date/time stamp line the WS class prints at the top of every page.
\def\ws@stamp{\today\hspace{2em}\jobname}
\newcommand{\wsstamp}[1]{\gdef\ws@stamp{#1}}

\renewcommand{\ps@headings}{%
  \renewcommand{\@oddhead}{\vbox to \headheight{%
     \hbox to \textwidth{\fontsize{7}{8}\selectfont\ws@stamp\hfil}\vss}%
     \llap{}\hfill}%
  \renewcommand{\@evenhead}{\@oddhead}%
  \renewcommand{\@oddfoot}{}\renewcommand{\@evenfoot}{}}

%% Running head is typeset by the class at the top of the text block instead of
%% in the header, matching the WS journal look (page no. + title / authors).
\newcommand{\ws@runhead}{}
\pagestyle{myheadings}
\renewcommand{\@oddhead}{\parbox[b]{\textwidth}{%
   \fontsize{7}{8}\selectfont\ws@stamp\par\vspace{6pt}%
   \fontsize{9}{11}\selectfont\itshape\hfill\ws@rightmark\hspace{1.5em}\upshape\thepage}}
\renewcommand{\@evenhead}{\parbox[b]{\textwidth}{%
   \fontsize{7}{8}\selectfont\ws@stamp\par\vspace{6pt}%
   \fontsize{9}{11}\selectfont\upshape\thepage\hspace{1.5em}\itshape\ws@leftmark\hfill}}
\renewcommand{\@oddfoot}{}
\renewcommand{\@evenfoot}{}

%% ------------------------------------------------------------- title material
\def\ws@authors{}
\def\ws@title{}
\renewcommand{\title}[1]{\gdef\ws@title{#1}}
%% Each block is self-contained: without the extra braces the \centering and
%% \itshape of the last \address would leak into the whole document body.
\renewcommand{\author}[1]{%
  \g@addto@macro\ws@authors{%
    \vspace{9pt}{\par\centering\fontsize{11}{13}\selectfont #1\par}}}
\newcommand{\address}[1]{%
  \g@addto@macro\ws@authors{%
    \vspace{2pt}{\par\centering\fontsize{9}{11}\selectfont\itshape #1\par}}}

\renewcommand{\maketitle}{%
  \thispagestyle{empty}%
  \vspace*{2pt}%
  {\fontsize{7}{8}\selectfont\ws@stamp\par}
  \vspace{34pt}%
  \begin{center}
    \fontsize{14}{17}\selectfont\bfseries\ws@title\par
  \end{center}
  \vspace{6pt}
  \ws@authors
  \vspace{10pt}\par}

%% ------------------------------------------------------------------- history
\newenvironment{history}
  {\vspace{10pt}\begin{center}\fontsize{9}{11}\selectfont}
  {\end{center}\vspace{2pt}}
\newcommand{\received}[1]{Received #1\par}
\newcommand{\revised}[1]{Revised #1\par}
\newcommand{\accepted}[1]{Accepted #1\par}
\newcommand{\published}[1]{Published #1\par}
\newcommand{\comby}[1]{Communicated by #1\par}

%% ------------------------------------------------------------------ abstract
\renewenvironment{abstract}
  {\vspace{6pt}\begin{list}{}{\setlength{\leftmargin}{2.5em}%
     \setlength{\rightmargin}{2.5em}\setlength{\listparindent}{14pt}}%
   \item[]\fontsize{9}{11.5}\selectfont}
  {\end{list}}

\newcommand{\keywords}[1]{%
  \vspace{6pt}\begin{list}{}{\setlength{\leftmargin}{2.5em}%
     \setlength{\rightmargin}{2.5em}}%
   \item[]\fontsize{9}{11.5}\selectfont\textit{Keywords}\/: #1\end{list}\vspace{4pt}}
\newcommand{\ccode}[1]{%
  \begin{list}{}{\setlength{\leftmargin}{2.5em}\setlength{\rightmargin}{2.5em}}%
   \item[]\fontsize{9}{11.5}\selectfont #1\end{list}}

%% ------------------------------------------------------------------ sections
\renewcommand{\section}{\@startsection{section}{1}{\z@}%
  {-14pt plus -2pt minus -2pt}{6pt}%
  {\fontsize{10}{12}\selectfont\bfseries}}
\renewcommand{\subsection}{\@startsection{subsection}{2}{\z@}%
  {-12pt plus -2pt minus -2pt}{5pt}%
  {\fontsize{10}{12}\selectfont\itshape}}
\renewcommand{\subsubsection}{\@startsection{subsubsection}{3}{\z@}%
  {-11pt plus -2pt minus -2pt}{4pt}%
  {\fontsize{10}{12}\selectfont\itshape}}
%% Headings read "3.5. Title"; \ref yields "3.5" without the trailing period.
\renewcommand{\thesection}{\arabic{section}}
\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}
\renewcommand{\@seccntformat}[1]{\csname the#1\endcsname.\hskip 0.5em}
\renewcommand{\theequation}{\arabic{equation}}

%% -------------------------------------------------------------------- floats
\renewcommand{\figurename}{Fig.}
\renewcommand{\tablename}{Table}
\long\def\@makecaption#1#2{%
  \vskip 6pt
  \setbox\@tempboxa\hbox{\fontsize{8}{10}\selectfont #1.\hskip 0.5em #2}%
  \ifdim\wd\@tempboxa >\hsize
    {\fontsize{8}{10}\selectfont #1.\hskip 0.5em #2\par}
  \else
    \hbox to\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip 4pt}

%% --------------------------------------------------- WS table conveniences
%% \tbl{<caption>}{<tabular>} -- caption above the table, as in the WS class.
\newcommand{\tbl}[2]{%
  \refstepcounter{table}%
  \begin{center}
  \parbox{\textwidth}{\fontsize{8}{10}\selectfont
     \setlength{\parindent}{0pt}Table~\thetable.\hskip 0.5em #1\par}
  \vspace{4pt}
  #2
  \end{center}}
%% booktabs supplies \toprule/\midrule/\bottomrule; WS names them differently.
\newcommand{\colrule}{\midrule}
\newcommand{\botrule}{\bottomrule}

%% ------------------------------------------------------- superscript citing
\renewcommand\@cite[2]{\textsuperscript{#1\if@tempswa , #2\fi}}
%% \citenum{key} -> bare number; \refcite{key} -> "Ref. n" (as in the WS class)
\DeclareRobustCommand{\citenum}[1]{%
  \begingroup\def\@cite##1##2{##1}\cite{#1}\endgroup}
\DeclareRobustCommand{\refcite}[1]{Ref.~\citenum{#1}}
\renewcommand\@biblabel[1]{#1.}
\renewcommand{\refname}{References}
\renewenvironment{thebibliography}[1]
  {\section*{\refname}%
   \fontsize{9}{11}\selectfont
   \list{\@biblabel{\@arabic\c@enumiv}}%
        {\settowidth\labelwidth{\@biblabel{#1}}%
         \leftmargin\labelwidth \advance\leftmargin\labelsep
         \setlength{\itemsep}{1pt}\setlength{\parsep}{0pt}
         \usecounter{enumiv}%
         \let\p@enumiv\@empty \renewcommand\theenumiv{\@arabic\c@enumiv}}%
   \sloppy\clubpenalty4000\@clubpenalty\clubpenalty\widowpenalty4000%
   \sfcode`\.\@m}
  {\def\@noitemerr{\@latex@warning{Empty `thebibliography' environment}}%
   \endlist}

\endinput
