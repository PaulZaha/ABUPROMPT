import pm4py

def prepare_bpmn(bpmn):
    # add missing gateway directions to bpmn
    gateways = [node for node in bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Gateway)]
    for gateway in gateways:
        if gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.UNSPECIFIED:
            in_arcs = gateway.get_in_arcs()
            out_arcs = gateway.get_out_arcs()
            len_in_arcs = len(in_arcs)
            len_out_arcs = len(out_arcs)
            if len_in_arcs > len_out_arcs:
                gateway._Gateway__gateway_direction = pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING
            elif len_in_arcs < len_out_arcs:
                gateway._Gateway__gateway_direction = pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING
            else:
                raise Exception("Gateway direction could not be determined")
    return bpmn