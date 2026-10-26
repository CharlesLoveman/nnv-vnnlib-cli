function [result, witness] = run_vnnlib_query(filepath, networks, opts)
  status = 2;
  property = load_vnnlib2(filepath);
  disp(property);
  networks = dictionary(networks);
  disp(networks);

  % Need to set this based on opts
  input_set = Star(property.lb, property.ub);
  disp(input_set);
 
  % 4. Configure verification
  reachOptions = struct;
  reachOptions.reachMethod = 'exact-star';
 
  if (numEntries(networks) ~= 1)
    % Handle multi-network
    return;
  end

  networks_values = values(networks);
  disp(networks_values);
  net = load_nnv_from_mat(networks_values(1));
 
  [result, witness] = net.verify_vnnlib(filepath, reachOptions);
  disp(result);
  disp(witness);
end
