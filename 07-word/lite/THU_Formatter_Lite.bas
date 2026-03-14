Attribute VB_Name = "THU_Formatter_Lite"
Option Explicit

' THU Formatter Lite (M0/M1 runnable baseline)
' Boundaries: deterministic format repair only, no content rewriting.

Private Const ENV_TEMPLATE_PATH As String = "THU_TEMPLATE_PATH"
Private Const TABLE_OUTER_WIDTH As Long = wdLineWidth150pt
Private Const TABLE_INNER_WIDTH As Long = wdLineWidth050pt

Public Sub OneClickDetectAndFix()
    Dim srcPath As String
    Dim fixedDocx As String
    Dim fixedPdf As String
    Dim logPath As String
    Dim headingFixCount As Long
    Dim bodyFixCount As Long
    Dim tableFixCount As Long
    Dim tableSkipCount As Long
    Dim tableWarnCount As Long
    Dim captionFixCount As Long
    Dim captionWarnCount As Long
    Dim inlineFixCount As Long
    Dim inlineWarnCount As Long

    srcPath = ActiveDocument.FullName
    If Len(srcPath) = 0 Then
        MsgBox "Please save document before running formatter.", vbExclamation
        Exit Sub
    End If

    fixedDocx = BuildOutputPath(srcPath, "_fixed.docx")
    fixedPdf = BuildOutputPath(srcPath, "_fixed.pdf")
    logPath = BuildOutputPath(srcPath, "_fix_log.txt")

    On Error GoTo Handler
    AppendLog logPath, "START: THU Formatter Lite"

    TemplateBinder logPath
    DocScanner logPath
    ApplyHeadingStyles logPath, headingFixCount
    NormalizeBody logPath, bodyFixCount
    EnsureCaptions logPath, captionFixCount, captionWarnCount, inlineFixCount, inlineWarnCount
    ApplyThreeLineTables logPath, tableFixCount, tableSkipCount, tableWarnCount
    RefreshFieldsAndToc logPath

    ActiveDocument.SaveAs2 FileName:=fixedDocx, FileFormat:=wdFormatXMLDocument
    ActiveDocument.ExportAsFixedFormat OutputFileName:=fixedPdf, ExportFormat:=wdExportFormatPDF

    AppendLog logPath, "SUMMARY: heading_fixed=" & CStr(headingFixCount) & _
        ", body_fixed=" & CStr(bodyFixCount) & _
        ", table_fixed=" & CStr(tableFixCount) & _
        ", table_skip=" & CStr(tableSkipCount) & _
        ", table_warn=" & CStr(tableWarnCount) & _
        ", caption_fixed=" & CStr(captionFixCount) & _
        ", caption_warn=" & CStr(captionWarnCount) & _
        ", inline_fixed=" & CStr(inlineFixCount) & _
        ", inline_warn=" & CStr(inlineWarnCount)
    AppendLog logPath, "DONE: exported docx/pdf"

    MsgBox "THU Formatter Lite finished." & vbCrLf & _
        "Fixed DOCX: " & fixedDocx & vbCrLf & _
        "Fixed PDF: " & fixedPdf, vbInformation
    Exit Sub

Handler:
    AppendLog logPath, "ERROR: " & CStr(Err.Number) & " - " & Err.Description
    MsgBox "Formatting failed: " & Err.Description, vbExclamation
End Sub

Private Function BuildOutputPath(ByVal srcPath As String, ByVal suffix As String) As String
    Dim dotPos As Long
    dotPos = InStrRev(srcPath, ".")
    If dotPos > 0 Then
        BuildOutputPath = Left$(srcPath, dotPos - 1) & suffix
    Else
        BuildOutputPath = srcPath & suffix
    End If
End Function

Private Sub TemplateBinder(ByVal logPath As String)
    Dim templatePath As String
    templatePath = Trim$(Environ$(ENV_TEMPLATE_PATH))

    If Len(templatePath) = 0 Then
        AppendLog logPath, "TEMPLATE: skip attach (env THU_TEMPLATE_PATH empty)"
        Exit Sub
    End If

    If Dir$(templatePath) = "" Then
        AppendLog logPath, "TEMPLATE: path not found: " & templatePath
        Exit Sub
    End If

    ActiveDocument.AttachedTemplate = templatePath
    ActiveDocument.UpdateStylesOnOpen = True
    AppendLog logPath, "TEMPLATE: attached " & templatePath
End Sub

Private Sub DocScanner(ByVal logPath As String)
    AppendLog logPath, "SCAN: paragraphs=" & CStr(ActiveDocument.Paragraphs.Count) & _
        ", tables=" & CStr(ActiveDocument.Tables.Count)
End Sub

Private Sub ApplyHeadingStyles(ByVal logPath As String, ByRef fixCount As Long)
    Dim p As Paragraph
    Dim t As String
    Dim rgx1 As Object
    Dim rgx2 As Object
    Dim rgx3 As Object

    Set rgx1 = CreateObject("VBScript.RegExp")
    rgx1.Pattern = "^\s*[0-9]+\s+"
    Set rgx2 = CreateObject("VBScript.RegExp")
    rgx2.Pattern = "^\s*[0-9]+\.[0-9]+\s+"
    Set rgx3 = CreateObject("VBScript.RegExp")
    rgx3.Pattern = "^\s*[0-9]+\.[0-9]+\.[0-9]+\s+"

    fixCount = 0
    For Each p In ActiveDocument.Paragraphs
        t = NormalizeParagraphText(p.Range.Text)

        If rgx3.Test(t) Then
            If p.Range.Style <> wdStyleHeading3 Then
                ApplyParagraphStyleStrict p, wdStyleHeading3
                fixCount = fixCount + 1
            End If
        ElseIf rgx2.Test(t) Then
            If p.Range.Style <> wdStyleHeading2 Then
                ApplyParagraphStyleStrict p, wdStyleHeading2
                fixCount = fixCount + 1
            End If
        ElseIf rgx1.Test(t) Then
            If p.Range.Style <> wdStyleHeading1 Then
                ApplyParagraphStyleStrict p, wdStyleHeading1
                fixCount = fixCount + 1
            End If
        End If
    Next p

    AppendLog logPath, "HEADING: converted=" & CStr(fixCount)
End Sub

Private Function NormalizeParagraphText(ByVal s As String) As String
    Dim t As String
    t = Replace$(s, vbCr, "")
    t = Replace$(t, Chr$(7), "")
    NormalizeParagraphText = Trim$(t)
End Function

Private Sub ClearManualOverrides(ByVal targetRange As Range)
    On Error Resume Next
    targetRange.Font.Reset
    targetRange.ParagraphFormat.Reset
    On Error GoTo 0
End Sub

Private Sub ApplyParagraphStyleStrict(ByVal p As Paragraph, ByVal styleValue As Variant)
    ClearManualOverrides p.Range
    p.Range.Style = styleValue
End Sub

Private Sub NormalizeBody(ByVal logPath As String, ByRef fixCount As Long)
    Dim p As Paragraph
    fixCount = 0

    For Each p In ActiveDocument.Paragraphs
        If p.Range.Information(wdWithInTable) Then
            GoTo ContinueLoop
        End If

        If p.Range.Style = wdStyleNormal Then
            With p.Format
                .LineSpacingRule = wdLineSpaceMultiple
                .LineSpacing = 24
                .FirstLineIndent = CentimetersToPoints(0.74)
                .SpaceBefore = 0
                .SpaceAfter = 0
            End With
            fixCount = fixCount + 1
        End If
ContinueLoop:
    Next p

    AppendLog logPath, "BODY: normalized=" & CStr(fixCount)
End Sub

Private Sub EnsureCaptions(ByVal logPath As String, ByRef fixCount As Long, ByRef warnCount As Long, ByRef inlineFixCount As Long, ByRef inlineWarnCount As Long)
    Dim p As Paragraph
    Dim t As String
    Dim kindText As String
    Dim titleText As String
    Dim bodyRange As Range
    Dim insertRange As Range

    fixCount = 0
    warnCount = 0
    inlineFixCount = 0
    inlineWarnCount = 0

    For Each p In ActiveDocument.Paragraphs
        t = NormalizeParagraphText(p.Range.Text)

        If p.Range.Information(wdWithInTable) Then
            GoTo ContinueCaptionLoop
        End If

        kindText = DetectCaptionKind(t)
        If Len(kindText) > 0 Then
            If Not TryApplyCaptionStyle(p) Then
                warnCount = warnCount + 1
            End If

            ConvertAnchoredShapesNearCaption p, inlineFixCount, inlineWarnCount

            If Not HasSequenceField(p.Range, kindText) Then
                titleText = ExtractCaptionTitle(t)

                Set bodyRange = p.Range.Duplicate
                bodyRange.End = bodyRange.End - 1
                bodyRange.Text = kindText & " "

                Set insertRange = bodyRange.Duplicate
                insertRange.Collapse wdCollapseEnd
                insertRange.Fields.Add insertRange, wdFieldSequence, kindText
                insertRange.InsertAfter " " & titleText

                fixCount = fixCount + 1
            End If

            If InStr(1, t, " ") = 0 And InStr(1, t, ChrW(&H3000)) = 0 Then
                warnCount = warnCount + 1
            End If
        End If

ContinueCaptionLoop:
    Next p

    AppendLog logPath, "CAPTION: fixed=" & CStr(fixCount) & ", warning_candidates=" & CStr(warnCount) & _
        ", inline_fixed=" & CStr(inlineFixCount) & ", inline_warn=" & CStr(inlineWarnCount)
End Sub

Private Function TryApplyCaptionStyle(ByVal p As Paragraph) As Boolean
    ClearManualOverrides p.Range

    On Error GoTo Fallback
    p.Range.Style = wdStyleCaption
    TryApplyCaptionStyle = True
    Exit Function

Fallback:
    On Error GoTo Failed
    p.Range.Style = "Caption"
    TryApplyCaptionStyle = True
    Exit Function

Failed:
    TryApplyCaptionStyle = False
End Function

Private Sub ConvertAnchoredShapesNearCaption(ByVal captionParagraph As Paragraph, ByRef fixCount As Long, ByRef warnCount As Long)
    Dim i As Long
    Dim shp As Shape
    Dim captionPos As Long
    Dim anchorPos As Long

    captionPos = captionParagraph.Range.Start

    For i = ActiveDocument.Shapes.Count To 1 Step -1
        Set shp = ActiveDocument.Shapes(i)
        anchorPos = shp.Anchor.Start

        If Abs(anchorPos - captionPos) <= 500 Then
            On Error GoTo ConvertFailed
            shp.ConvertToInlineShape
            fixCount = fixCount + 1
            On Error GoTo 0
        End If
ContinueShapeLoop:
    Next i
    Exit Sub

ConvertFailed:
    warnCount = warnCount + 1
    On Error GoTo 0
    Resume ContinueShapeLoop
End Sub

Private Function DetectCaptionKind(ByVal textLine As String) As String
    Dim rgx As Object

    Set rgx = CreateObject("VBScript.RegExp")
    rgx.IgnoreCase = False
    rgx.Global = False
    rgx.Pattern = "^\s*图\s*[0-9]+([-.][0-9]+)*\s+"
    If rgx.Test(textLine) Then
        DetectCaptionKind = "图"
        Exit Function
    End If

    rgx.Pattern = "^\s*表\s*[0-9]+([-.][0-9]+)*\s+"
    If rgx.Test(textLine) Then
        DetectCaptionKind = "表"
        Exit Function
    End If

    DetectCaptionKind = ""
End Function

Private Function ExtractCaptionTitle(ByVal textLine As String) As String
    Dim rgx As Object
    Dim resultText As String

    Set rgx = CreateObject("VBScript.RegExp")
    rgx.IgnoreCase = False
    rgx.Global = False
    rgx.Pattern = "^\s*[图表]\s*[0-9]+([-.][0-9]+)*\s*"

    resultText = rgx.Replace(textLine, "")
    resultText = Trim$(resultText)
    If Len(resultText) = 0 Then
        resultText = "题注"
    End If

    ExtractCaptionTitle = resultText
End Function

Private Function HasSequenceField(ByVal targetRange As Range, ByVal captionKind As String) As Boolean
    Dim f As Field
    Dim codeText As String

    For Each f In targetRange.Fields
        If f.Type = wdFieldSequence Then
            codeText = LCase$(f.Code.Text)
            If InStr(1, codeText, LCase$(captionKind), vbTextCompare) > 0 Then
                HasSequenceField = True
                Exit Function
            End If
        End If
    Next f

    HasSequenceField = False
End Function

Private Sub ApplyThreeLineTables(ByVal logPath As String, ByRef fixCount As Long, ByRef skipCount As Long, ByRef warnCount As Long)
    Dim tbl As Table
    Dim rowIndex As Long

    fixCount = 0
    skipCount = 0
    warnCount = 0

    For Each tbl In ActiveDocument.Tables
        If ShouldSkipTable(tbl) Then
            skipCount = skipCount + 1
            GoTo ContinueTable
        End If

        On Error GoTo TableFailed

        tbl.Borders.Enable = False

        For rowIndex = 1 To tbl.Rows.Count
            tbl.Rows(rowIndex).Borders(wdBorderTop).LineStyle = wdLineStyleNone
            tbl.Rows(rowIndex).Borders(wdBorderBottom).LineStyle = wdLineStyleNone
        Next rowIndex

        ApplyHorizontalBorder tbl.Rows(1).Borders(wdBorderTop), wdLineStyleSingle, TABLE_OUTER_WIDTH
        ApplyHorizontalBorder tbl.Rows(1).Borders(wdBorderBottom), wdLineStyleSingle, TABLE_INNER_WIDTH
        tbl.Rows(1).HeadingFormat = True
        ApplyHorizontalBorder tbl.Rows(tbl.Rows.Count).Borders(wdBorderBottom), wdLineStyleSingle, TABLE_OUTER_WIDTH

        fixCount = fixCount + 1
        On Error GoTo 0
        GoTo ContinueTable

TableFailed:
        warnCount = warnCount + 1
        On Error GoTo 0
ContinueTable:
    Next tbl

    AppendLog logPath, "TABLE: three_line_applied=" & CStr(fixCount) & _
        ", skipped=" & CStr(skipCount) & ", warnings=" & CStr(warnCount)
End Sub

Private Sub ApplyHorizontalBorder(ByVal borderObj As Border, ByVal lineStyle As WdLineStyle, ByVal lineWidth As WdLineWidth)
    borderObj.LineStyle = lineStyle
    borderObj.LineWidth = lineWidth
End Sub

Private Function ShouldSkipTable(ByVal tbl As Table) As Boolean
    If tbl.Rows.Count = 0 Then
        ShouldSkipTable = True
        Exit Function
    End If

    If tbl.NestingLevel > 1 Then
        ShouldSkipTable = True
        Exit Function
    End If

    ShouldSkipTable = False
End Function

Private Sub RefreshFieldsAndToc(ByVal logPath As String)
    Dim toc As TableOfContents
    Dim tof As TableOfFigures

    ActiveDocument.Fields.Update

    For Each toc In ActiveDocument.TablesOfContents
        toc.Update
    Next toc

    For Each tof In ActiveDocument.TablesOfFigures
        tof.Update
    Next tof

    AppendLog logPath, "FIELD: fields/toc/tof updated"
End Sub

Private Sub AppendLog(ByVal logPath As String, ByVal lineText As String)
    Dim ff As Integer
    ff = FreeFile
    Open logPath For Append As #ff
    Print #ff, Format$(Now, "yyyy-mm-dd hh:nn:ss") & " | " & lineText
    Close #ff
End Sub
