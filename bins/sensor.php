<?php
    $action = $_REQUEST['action'];
    $sensorcli = 'python sensorcli.py ';
    try {
        switch ($action) {
            case 'get_data':
                //$cmd='python3 test.py';
                $cmd=$sensorcli.'get_data '.' '.$_REQUEST['songid'].' '.$_REQUEST['startmsec'].' '.$_REQUEST['endmsec'];
                exec($cmd,$out,$states);
                print  $out[0];
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