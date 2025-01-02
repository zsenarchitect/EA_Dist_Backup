(defun c:EA_EXPLODE_ALL_BLOCKS ( / explode layouts )
   (setq layouts (vla-get-layouts (vla-get-activedocument (vlax-get-acad-object)))
         explode t
   )
   (while explode
       (setq explode nil)
       (vlax-for layout layouts
           (vlax-for obj (vla-get-block layout)
               (and
                   (= "AcDbBlockReference" (vla-get-objectname obj))
                   (not (vl-catch-all-error-p (vl-catch-all-apply 'vla-explode (list obj))))
                   (not (vl-catch-all-error-p (vl-catch-all-apply 'vla-delete  (list obj))))
                   (setq explode t)
               )
           )
       )
   )
   (princ)
)
(vl-load-com) (princ)















(defun c:EA_DELETE_ALL_SOLID_HATCH ( / d )
    (vlax-for b (vla-get-blocks (setq d (vla-get-activedocument (vlax-get-acad-object))))
        (if (= :vlax-false (vla-get-isxref b))
            (vlax-for o b
                (if (and (= "AcDbHatch" (vla-get-objectname o))
                         (= "SOLID" (strcase (vla-get-patternname o)))
                         (vlax-write-enabled-p o)
                    )
                    (vla-delete o)
                )
            )
        )
    )
    (vla-regen d acallviewports)
    (princ)
)
(vl-load-com) (princ)

























;;  AllColorBylayer.lsp [command name: ACB]
;;  To change the Color of ALL entities in the drawing, including those nested in
;;    Block definitions [but not Xrefs] and Dimension/Leader parts, to ByLayer.
;;  Kent Cooper, 27 February 2014, expanding on some elements by p_mcknight

 

(vl-load-com)
(defun C:EA_ALL_COLOR_BY_LAYER ; = All to Color Bylayer
  (/ cb ent obj blk subent)
  (defun cb () ; = force Color(s) to Bylayer
    (setq obj (vlax-ename->vla-object ent))
    (vla-put-color obj 256); ByLayer
    (if (wcmatch (vla-get-ObjectName obj) "*Dimension,*Leader")
      (foreach prop '(DimensionLineColor ExtensionLineColor TextColor)
        ;; not all such entity types have all 3 properties, but all have at least one
        (if (vlax-property-available-p obj prop)
          (vlax-put obj prop 256); ByLayer
        ); if
      ); foreach
    ); if
  ); defun -- cb
;;  Top-level entities:
  (setq ent (entnext))
  (while ent
    (cb)
    (setq ent (entnext ent))
  ); while
;;  Nested entities in this drawing's Block definitions:
  (setq blk (tblnext "block" t))
  (while blk
    (if (= (logand 20 (cdr (assoc 70 blk))) 0); not an Xref [4] or Xref-dependent [16]
      (progn
        (setq ent (cdr (assoc -2 blk)))
        (while ent
          (cb)
          (setq ent (entnext ent))
        ); while
      ); progn
    ); if
    (setq blk (tblnext "block"))
  ); while
  (command "_.regenall")
  (princ)
); defun









(defun c:EA_REMOVE_ALL_DIM (/ aDoc)
  (setq aDoc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (if (tblsearch "DIMSTYLE" "Standard")
    (command "-DIMSTYLE" "R" "Standard")
  )

  (vlax-for blk	(vla-get-blocks aDoc)
    (if
      (eq :vlax-false (vla-get-isXref blk))
       (vlax-for h blk
	 (cond
	   ((and (vlax-write-enabled-p h)
		 (vl-string-search "Dimension" (vla-get-ObjectName h))
	    )
	    (vla-delete h)
	   )

	 )
       )
    )
  )
  (repeat 4 (vla-purgeall aDoc))
)
(vl-load-com)





(defun c:EA_CLEAN_CAD_FOR_REVIT ( / d )

   
   (c:EA_DELETE_ALL_SOLID_HATCH)
   (c:EA_REMOVE_ALL_DIM )
   (c:EA_EXPLODE_NON_SOLID_HATCH )
   (C:EA_ALL_COLOR_BY_LAYER)
)


(defun c:EA_CLEAN_CAD_FOR_RHINO ( / d )

   
   (c:EA_DELETE_ALL_SOLID_HATCH)
   (c:EA_REMOVE_ALL_DIM )
   (c:EA_EXPLODE_ALL_BLOCKS)
   (c:EA_EXPLODE_NON_SOLID_HATCH )
   (C:EA_ALL_COLOR_BY_LAYER)
)



(defun c:EA_EXPLODE_NON_SOLID_HATCH ( / )
(mapcar '(lambda (x)
(command "explode" x)
) (mapcar 'cadr (ssnamex (ssget "_x" '((0 . "HATCH")(2 . "~SOLID")))))))




(defun try (func inputs / result)
  (if (not (vl-catch-all-error-p (setq result (vl-catch-all-apply func inputs))))
    result))

(defun c:EA_SET_HATCH_SCALE ( / d )
    (vlax-for b (vla-get-blocks (setq d (vla-get-activedocument (vlax-get-acad-object))))
        (if (= :vlax-false (vla-get-isxref b))
            (vlax-for o b
                (if (and (= "AcDbHatch" (vla-get-objectname o))
                         (/= "SOLID" (strcase (vla-get-patternname o)))
                         (vlax-write-enabled-p o)
                    )

                    ;;(command "explode" o)
		    ;;(vl-catch-all-apply 'setpropertyvalue'(list o "PatternScale" 50))
                    ;;(try setpropertyvalue (list o "PatternScale" 100))
                    ;;(setq errorobj (vl-catch-all-apply (lambda (x)(setpropertyvalue x "PatternScale" 100))o))
                )
            )
        )
    )
    (vla-regen d acallviewports)
    (princ)
)
(vl-load-com) (princ)

