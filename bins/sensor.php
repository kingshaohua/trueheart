<?php
    $action = $_REQUEST['action'];
    $sensorcli = 'python sensorcli.py ';
    try {
        switch ($action) {

            case 'get_data':
                exec($sensorcli.'get_data '.
                ' '.$_REQUEST['songname'].
                ' '.$_REQUEST['startmsec'].
                ' '.$_REQUEST['endmsec'],$out,$states);
                print $out[0];
                break;
            default:
                print 'unkown cmd'.$action;
                # code...
                break;
        }
    } catch (Exception $e) {
        echo $e->getMessage();
    }

?>